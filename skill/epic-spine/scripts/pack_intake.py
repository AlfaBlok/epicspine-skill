#!/usr/bin/env python3
"""Wake text, `pack.py <name> --wake-text [--role R]`: the desk intake rule (references/packs.md "Desk intake") and, per
persona, what its role may write (`role_text`, "Persona wake text").

A pack's `intake` says, per kind: how to recognise it, the pack sections or fields it lands in (`targets`; or an
`external` target such as a new child spine), the role that writes it, and the reply naming where it landed. `check()`
proves every target resolves and its writer may write it (pack.py check runs it); `wake_text()` renders the rule as the
Markdown a console pastes into a desk persona's prompt.
"""
from __future__ import annotations

import argparse
import re
import sys

import pack


def anchor(heading: str | None) -> str:
    """GitHub's heading anchor: `Points to emphasize` -> `#points-to-emphasize`; no heading (the file's one table) -> ``."""
    if not heading:
        return ""
    return "#" + re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", heading.strip().lower()))


def landing(schema: dict, target: str) -> tuple[str, str]:
    """(label, `path#anchor`) of an intake target: a section `file.section`, a field `file.section.field`, or an external key."""
    ext = schema["intake"].get("external", {})
    if target in ext:
        return target, ext[target].get("path", "")
    fkey, skey = target.split(".")[:2]
    f = schema["files"][fkey]
    s = f["sections"][skey]
    path = s.get("path", f["path"])
    label = f"{fkey} › {s['heading']}" if s.get("heading") else fkey
    if target.count(".") == 2:
        label += f" › {s['fields'][target.split('.')[2]]['column']}"
    return label, path + anchor(s.get("heading"))


def may_write(schema: dict, target: str, role: str) -> bool:
    ext = schema["intake"].get("external", {})
    if target in ext:
        return role in ext[target].get("writers", [])
    if target.count(".") == 2:
        return role in pack.field_writers(schema, target)
    fkey, skey = target.split(".")
    s = schema["files"][fkey]["sections"][skey]
    return role in s.get("writers", []) or role in s.get("add_rows", [])


def check(schema: dict) -> list[str]:
    """Errors in a pack's `intake`; none when it has no intake."""
    intake = schema.get("intake")
    if intake is None:
        return []
    errs: list[str] = []
    secs = dict(pack.sections(schema))
    flds = pack.fields(schema)
    ext = intake.get("external", {})
    clash = sorted(set(ext) & (set(secs) | set(flds)))
    errs.extend(f"intake: external {k} shadows a pack address" for k in clash)
    if not intake.get("kinds"):
        errs.append("intake: no kinds")
    for kkey, k in intake.get("kinds", {}).items():
        tag = f"intake {kkey}"
        errs.extend(f"{tag}: no {a}" for a in ("label", "recognise", "targets", "writer", "reply") if not k.get(a))
        writer = k.get("writer")
        for t in k.get("targets", []):
            if t not in secs and t not in flds and t not in ext:
                errs.append(f"{tag}: target {t} does not resolve (not a section, field or external)")
            elif writer and not may_write(schema, t, writer):
                errs.append(f"{tag}: {writer} may not write {t}")
        if "{link}" not in k.get("reply", "{link}"):
            errs.append(f"{tag}: reply does not name where it landed ({{link}})")
        for faddr, value in k.get("set", {}).items():
            fld = flds.get(faddr)
            if fld is None:
                errs.append(f"{tag}: set {faddr} is not a field")
                continue
            if ".".join(faddr.split(".")[:2]) not in k.get("targets", []):
                errs.append(f"{tag}: set {faddr} is outside its targets")
            allowed = fld.get("values") or list(schema["lifecycles"].get(fld.get("lifecycle"), {}).get("states", {}))
            if fld.get("type") == "role":
                allowed = list(schema["roles"])
            if allowed and value not in allowed:
                errs.append(f"{tag}: set {faddr} = {value} not one of {allowed}")
    return errs


def wake_text(schema: dict) -> str:
    """The intake rule as Markdown for a desk persona's wake prompt: one block per kind, then how to reply."""
    intake = schema["intake"]
    kinds = intake["kinds"]
    out = [
        f"## Desk intake (pack {schema['pack']}): {len(kinds)} kinds",
        intake["doc"],
        "",
    ]
    for n, (key, k) in enumerate(kinds.items(), 1):
        out.append(f"{n}. **{k['label']}** (`{key}`): {k['recognise']}." + (f" E.g. \"{k['example']}\"." if k.get("example") else ""))
        lands = "; ".join(f"{label} → `{link}`" for label, link in (landing(schema, t) for t in k["targets"]))
        out.append(f"   - Lands in: {lands}")
        if k.get("set"):
            out.append("   - Set: " + ", ".join(f"{a.split('.')[-1]} = {v}" for a, v in k["set"].items()))
        out.append(f"   - Written as: {k['writer']}" + (f"; then {k['acts']}" if k.get("acts") else "") + (f". Jordi sees it on: {k['screen']}" if k.get("screen") else ""))
        out.append(f"   - Reply: {k['reply']}")
    ext = intake.get("external", {})
    out += [
        "",
        "Each thing Jordi says is one kind and one write; a line that says two things (a priority and a key message) is two writes, one reply line each. " + intake.get("unsure", ""),
        intake.get("reply", ""),
        "Links are repo paths with the section's anchor; a table row links its line instead (`<path>#L<n>`). Give them as links to the file on GitHub (`https://github.com/<owner>/<repo>/blob/main/<path>#anchor`) when the repo has a remote.",
    ]
    out += [f"External target `{key}`: {e['doc']}" + (f" (`{e['path']}`)" if e.get("path") else "") + "." for key, e in ext.items()]
    return "\n".join(out).rstrip() + "\n"


def _path(f: dict, s: dict) -> str:
    return f"`{s.get('path', f['path']).replace('{date}', '<date>')}`"


def _where(f: dict, s: dict) -> str:
    return _path(f, s) + (f" › {s['heading']}" if s.get("heading") else "")


def _writes(schema: dict, role: str) -> list[str]:
    """One line per pack section the role may write: the whole section, row adds, the columns it owns, status moves."""
    moved = {lc["field"] for lc in schema["lifecycles"].values() if any(role in t["by"] for t in lc["transitions"])}
    out: dict[tuple[str, str], list[str]] = {}
    for fkey, f in schema["files"].items():
        for skey, s in f["sections"].items():
            cols = {k: v["column"] for k, v in s.get("fields", {}).items() if "computed" not in v and "lifecycle" not in v}
            mine = [c for k, c in cols.items() if role in pack.field_writers(schema, f"{fkey}.{skey}.{k}")]
            how = []
            if role in s.get("add_rows", []):
                how.append("replace the table each run" if s.get("rows") == "replace" else "add rows")
            if not cols and role in s.get("writers", []):
                how.append("edit")
            elif mine and len(mine) == len(cols):
                how.append("edit every column")
            elif mine:
                rest = [c for c in cols.values() if c not in mine]
                how.append("edit every column but " + ", ".join(rest) if len(rest) < len(mine) else "edit only " + ", ".join(mine))
            if any(fld.startswith(f"{fkey}.{skey}.") for fld in moved):
                how.append("move the status (below)")
            if how:
                out.setdefault((_path(f, s), "; ".join(how)), []).append(s.get("heading") or "")
    return [f"- {p}" + (" › " + ", ".join(h) if all(h) else "") + f": {how}" for (p, how), h in out.items()]


def role_text(schema: dict, role: str) -> str:
    """What one persona may do, from the schema alone, as Markdown for its wake prompt: duty, writable targets, status
    moves with their checks, the hold / approval rules that bind it, the commit signature. `role` is a key of `roles`."""
    owner = schema.get("owner")
    out = [f"## Pack {schema['pack']}: you are the {role}", schema["roles"][role].rstrip(".") + ".", "", "You may write (everything else in the pack files is read-only for you):"]
    out += _writes(schema, role) or ["- nothing in the pack files"]
    used: dict[str, dict] = {}
    moves: list[str] = []
    bind: list[str] = []
    for name, lc in schema["lifecycles"].items():
        plain: list[str] = []
        for t in (t for t in lc["transitions"] if role in t["by"]):
            ck = [k for k, c in schema["checks"].items() if f"{t['from']}>{t['to']}" in c.get("at", [])]
            used.update({k: schema["checks"][k] for k in ck})
            names = [k + (f" ({'/'.join(schema['checks'][k]['platforms'])})" if schema["checks"][k].get("platforms") else "") for k in ck]
            step = f"`{t['from']} → {t['to']}`"
            if t.get("when") or t.get("kinds") or ck:
                moves.append(f"- {name} {step}" + (f" ({', '.join(t['kinds'])} rows)" if t.get("kinds") else "") + (f": {t['when']}" if t.get("when") else "") + (f"; checks: {', '.join(names)}" if ck else ""))
            else:
                plain.append(step)
        if plain:
            moves.append(f"- {name} " + ", ".join(plain))
        if "held" in lc["states"] and any(role in t["by"] and t["to"] == "held" for t in lc["transitions"]):
            src = used["hold_rules"]["source"].split(".") if "hold_rules" in used else None
            bind.append("- A draft matching a hold rule" + (f" ({_where(schema['files'][src[0]], schema['files'][src[0]]['sections'][src[1]])})" if src else "") + " goes to `held`, never `scheduled`; " + "; ".join(f"`{t['from']} → {t['to']}` is {'/'.join(t['by'])}'s alone" for t in lc["transitions"] if t["from"] == "held" and role not in t["by"] and t["to"] != "pulled") + ".")
        if "pulled" in lc["states"] and owner and role != owner and any(role in t["by"] for t in lc["transitions"]):
            bind.append(f"- {owner} may pull a {name} (`pulled`): never act on a pulled one.")
    bind += [f"- {r['doc']} (by {r['by']}; undo: {r['undo']})" for r in schema.get("rules", {}).values() if r.get("by") == role]
    bind += [f"- Effect `{k}`: {v}" for k, v in schema.get("effects", {}).items() if role in v]
    if schema.get("approval_gate"):
        bind.append(f"- Nothing goes out without {owner}'s approval.")
    out += ["", "Status moves you may make (any other change of a status cell is illegal):"] + (moves or ["- none"])
    if used:
        out += ["", "Checks the hook runs on those moves:"] + [f"- `{k}`: {c['doc']}" for k, c in used.items()]
    if bind:
        out += ["", "Rules that bind you:"] + bind
    out += ["", f"Every step is a commit signed `Persona: {role}` (`EPICSPINE_PERSONA={role}`); the hook rejects an illegal transition."]
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="pack.py <name>", description="Print a pack's wake text: the desk intake rule, or one role's duties.")
    ap.add_argument("name", choices=pack.available())
    ap.add_argument("--wake-text", action="store_true", required=True)
    ap.add_argument("--role", help="the persona's role in the pack (default: the desk intake rule, which the owner gets too)")
    a = ap.parse_args(argv)
    schema = pack.load(a.name)
    if a.role and a.role.lower() != str(schema.get("owner", "")).lower():
        role = next((r for r in schema["roles"] if r.lower() == a.role.lower()), None)
        if role is None:
            print(f"pack {a.name} has no role {a.role}; roles: {', '.join(schema['roles'])}", file=sys.stderr)
            return 2
        sys.stdout.write(role_text(schema, role))
        return 0
    if "intake" not in schema:
        print(f"pack {a.name} has no intake", file=sys.stderr)
        return 1
    sys.stdout.write(wake_text(schema))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
