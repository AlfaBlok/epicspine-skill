"""Validate a pack-enabled repo's pack files against the schema (references/packs.md "Validate").

  pack.py validate [--repo PATH] [--staged] [--by ROLE] [--message FILE]

Checks each pack file present: its sections and required columns (computed ones excepted), enum and id values, and, row
by row against HEAD, that a status change is a path of listed transitions (kind-matched; made by the writer's role when
the writer is known), that rows are not removed, and the `checks` run at the transitions the row passed (link rule,
disclosure, never-say, caps, hold rules, link present). The writer is `--by`, else `EPICSPINE_PERSONA`, else a
`Persona:` trailer in `--message`; with none, only legality is checked, not who. The commit hook runs `staged()`."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from collections import deque
from pathlib import Path

import pack
import pack_md as md
from pack_checks import run_check

def role_of(schema: dict, by: str | None = None, message: str | None = None) -> tuple[str | None, str | None]:
    """(role, issue): the writer's pack role, or None when unknown; an issue when it names no role of the pack."""
    raw = by or os.environ.get("EPICSPINE_PERSONA", "")
    if not raw and message and (m := re.search(r"^Persona:\s*(.+?)\s*$", message, re.M | re.I)):
        raw = m.group(1)
    if not raw.strip():
        return None, None
    hit = next((r for r in schema["roles"] if r.lower() == raw.strip().lower()), None)
    return hit, None if hit else f"writer {raw.strip()!r} is not a role of pack {schema['pack']} ({', '.join(schema['roles'])})"


def route(lc: dict, prev: str | None, to: str, kind: str | None, role: str | None) -> list[tuple[str, str]] | None:
    """Steps of the shortest legal path prev -> to (a new row starts at `initial` or one of its first steps); None if none."""
    ok = [t for t in lc["transitions"] if (not t.get("kinds") or kind in t["kinds"]) and (role is None or role in t["by"])]
    starts = [prev] if prev else [lc["initial"]] + [t["to"] for t in lc["transitions"] if t["from"] == lc["initial"]]
    for start in starts:
        back, todo = {start: None}, deque([start])
        while todo:
            cur = todo.popleft()
            if cur == to:
                steps = []
                while back[cur]:
                    steps.append((back[cur], cur))
                    cur = back[cur]
                return steps[::-1]
            for t in ok:
                if t["from"] == cur and t["to"] not in back:
                    back[t["to"]] = cur
                    todo.append(t["to"])
    return None


def check_section(schema: dict, s: dict, at: str, new: str, old: str | None, role: str | None, source) -> list[str]:
    tag = f"{at} ## {s['heading']}" if s["heading"] else at
    text = md.body(new, s["heading"])
    if text is None:
        return [f"{at}: missing section ## {s['heading']} (pack.py init adds it)"]
    who = set(s.get("writers", [])) | set(s.get("add_rows", []))
    if s["shape"] != "table":
        changed = (md.body(old, s["heading"]) or "").strip() != text.strip()
        return [f"{tag}: {role} may not write it" ] if role and changed and role not in who else []
    tbl, flds = md.table(text), s["fields"]
    if not tbl:
        return [f"{tag}: no table (pack.py init writes its header)"]
    head, raw = tbl
    gone = [f["column"] for f in flds.values() if "computed" not in f and f["column"] not in head]
    if gone:
        return [f"{tag}: missing column(s) {', '.join(gone)}"]
    recs = [{k: r.get(f["column"], "") for k, f in flds.items()} for r in raw]
    otbl = md.table(md.body(old, s["heading"]))
    idk = next((k for k, f in flds.items() if f["type"] == "id"), None)
    # HEAD's table without the id column is the conversion to the pack (pack init + reshape): no row to compare against
    olds = [{k: r.get(f["column"], "") for k, f in flds.items()} for r in otbl[1]] if otbl and (not idk or flds[idk]["column"] in otbl[0]) else []
    convert = bool(otbl and otbl[1]) and not olds
    lk = next((k for k, f in flds.items() if "lifecycle" in f), None)
    lc = schema["lifecycles"].get(flds[lk]["lifecycle"]) if lk else None
    out, seen = [], set()
    if not idk:
        return [f"{tag}: {role} may not write it"] if role and recs != olds and role not in who else []
    by_id = {r[idk]: r for r in olds}
    on = schema.get("checks", {}).get("transitions", {}).get("on", list(schema["lifecycles"]))
    for i, rec in enumerate(recs):
        rid = rec[idk] or f"row {i + 1}"
        say = lambda m: out.append(f"{tag} {rid}: {m}")  # noqa: E731
        if not rec[idk] or not re.fullmatch(flds[idk].get("pattern", ".+"), rec[idk]):
            say(f"{flds[idk]['column']} {rec[idk]!r} does not match {flds[idk].get('pattern')}")
        if rec[idk] in seen:
            say("duplicate id")
        seen.add(rec[idk])
        for k, f in flds.items():
            vals = f.get("values") or (list(schema["lifecycles"][f["lifecycle"]]["states"]) if "lifecycle" in f else None)
            if vals and rec[k] and rec[k].lower() not in [v.lower() for v in vals]:
                say(f"{f['column']} {rec[k]!r} not one of {', '.join(vals)}")
        prev = by_id.get(rec[idk])
        if role and prev is None and role not in s.get("add_rows", []):
            say(f"{role} may not add rows")
        if role and prev:
            for k in flds:
                if k != lk and rec[k] != prev[k] and role not in pack.field_writers(schema, f"{at_key(schema, s)}.{k}"):
                    say(f"{role} may not write {flds[k]['column']}")
        if not lc or flds[lk]["lifecycle"] not in on or convert:
            continue
        status, was = rec[lk].lower(), prev[lk].lower() if prev else None
        if not status:
            say(f"no {flds[lk]['column']}")
            continue
        if status == was or status not in lc["states"]:
            continue
        kind = rec.get(lc["kind_field"].split(".")[-1], "").lower() if lc.get("kind_field") else None
        steps = route(lc, was, status, kind, role)
        if steps is None:
            say(f"illegal {flds[lk]['column'].lower()} change {was or 'new row'} -> {status}" + (f" by {role}" if role else "") + (f" (kind {kind})" if kind else ""))
            continue
        passed = {f"{a}>{b}" for a, b in steps}
        targets = [b for a, b in steps]
        live = set(lc["path"][min([lc["path"].index(t) for t in targets if t in lc["path"]] or [len(lc["path"])]):])
        ctx = {"rows": recs, "status": lk, "live": live, "source": source}
        for key, c in schema.get("checks", {}).items():
            plats = [x.lower() for x in c.get("platforms", [])]
            kinds = [x.lower() for x in c.get("kinds", [])]
            if passed & set(c.get("at", [])) and (not plats or rec.get("platform", "").lower() in plats) and (not kinds or kind in kinds):
                for m in run_check(key, c, rec, ctx):
                    say(f"{key}: {m}")
    if lc and s.get("rows") != "replace":
        out += [f"{tag} {r[idk]}: row removed (rows are never deleted; set a status instead)" for r in olds if r[idk] not in seen]
    return out


def at_key(schema: dict, s: dict) -> str:
    return next(f"{fk}.{sk}" for fk, f in schema["files"].items() for sk, x in f["sections"].items() if x is s)


def validate(schema: dict, repo: Path, new, old, role: str | None = None, only: set[str] | None = None) -> list[str]:
    """Issues in the pack files `new` reads (vs `old`); `only` limits it to those repo paths (the staged ones)."""
    def source(addr: str) -> list:
        fk, sk = addr.split(".")
        s = schema["files"][fk]["sections"][sk]
        text = md.body(new(md.where(schema["files"][fk], s)), s["heading"])
        if s["shape"] != "table":
            return md.items(text)
        tbl = md.table(text)
        return [{k: r.get(f["column"], "") for k, f in s["fields"].items()} for r in (tbl[1] if tbl else [])]
    out = []
    for f in schema["files"].values():
        for s in f["sections"].values():
            path = md.where(f, s)
            paths = [p for p in only if re.fullmatch(re.escape(path).replace(r"\{date\}", r"[^/]+"), p)] if f.get("many") and only is not None \
                else sorted(str(p.relative_to(repo)) for p in repo.glob(path.replace("{date}", "*"))) if f.get("many") else [path]
            for p in paths:
                if (only is None or p in only) and (text := new(p)) is not None:
                    out += check_section(schema, s, p, text, old(p), role, source)
    return out


def run(repo: Path, staged: bool, by: str | None = None, message: str | None = None) -> list[str]:
    """Issues for each pack the repo turns on ([] for a repo with none): the staged pack files against HEAD (the commit
    hook), else the working tree's; a writer that names no role is an issue only when a pack file is in play."""
    names = [n for n in pack.enabled(repo) if n in pack.available()]
    if not names:
        return []
    only = set(filter(None, subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
                                           capture_output=True, text=True).stdout.split("\0"))) if staged else None
    out = []
    for name in names:
        schema = pack.load(name)
        role, bad = role_of(schema, by, message)
        new = md.git_reader(repo, "") if staged else md.worktree(repo)
        issues = validate(schema, repo, new, md.git_reader(repo, "HEAD"), role, only)
        touched = only is None or any(md.where(f, s) in only or f.get("many") for f in schema["files"].values() for s in f["sections"].values())
        out += [f"pack {name}: {i}" for i in ([bad] if bad and touched else []) + issues]
    return out


def staged(repo: Path) -> list[str]:
    """The commit hook (pre_commit.py): the staged pack files' issues, one line each."""
    return run(repo, True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pack.py validate", description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--staged", action="store_true", help="the index against HEAD, as the commit hook does")
    ap.add_argument("--by", help="the writer's role (else EPICSPINE_PERSONA, else a Persona: trailer in --message)")
    ap.add_argument("--message", type=Path, help="a commit message file to read the Persona: trailer from")
    a = ap.parse_args(argv)
    repo = a.repo.resolve()
    issues = run(repo, a.staged, a.by, a.message.read_text(encoding="utf-8") if a.message else None)
    print("\n".join(issues) if issues else f"ok ({', '.join(pack.enabled(repo)) or 'no pack on'})")
    return 1 if issues else 0
