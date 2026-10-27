#!/usr/bin/env python3
"""Pack export, `pack.py <name> --json [--repo PATH]`: one JSON document of a repo's pack data (references/packs.md).

Reads every file and section the pack's schema names (a section may live in another file, e.g.
the root spine), tables by column header, computes back-links (`computed: {from: ...}`) and never
crashes on bad data: anything it cannot read is a `warnings` entry and an empty value.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pack

EXPORT_VERSION = 1
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
SEP = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
URL = re.compile(r"https?://[^\s)\]>|]+")
NUM = re.compile(r"^\s*(-?\d+(?:\.\d+)?)")
EMPTY = {"", "-", "—", "–", "none", "n/a"}
DATES = {"date": r"\d{4}-\d{2}-\d{2}", "month": r"\d{4}-\d{2}", "datetime": r"\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}.*)?"}


def cells(line: str) -> list[str]:
    """A table row's cells; `\\|` is a literal pipe; a missing outer pipe is tolerated."""
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", body)]


def block(lines: list[str], heading: str | None) -> tuple[int, list[str]] | None:
    """(offset, body lines) under `heading` up to the next heading of its level or higher; None = absent."""
    if heading is None:
        return 0, lines
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m and m.group(2).strip().lower() == heading.lower():
            end = next((j for j in range(i + 1, len(lines)) if (h := HEADING.match(lines[j])) and len(h.group(1)) <= len(m.group(1))), len(lines))
            return i + 1, lines[i + 1:end]
    return None


def coerce(fld: dict, raw: str, states: list[str]):
    """(value, problem or None) for one cell by the field's type."""
    t, v = fld["type"], raw.strip()
    if t in ("ref", "refs"):
        ids = [x for x in re.split(r"[,;\s·]+", v) if x.lower() not in EMPTY]
        return (ids if t == "refs" else (ids[0] if ids else None)), None
    if v.lower() in EMPTY:
        return None, None
    if t in ("number", "percent"):
        m = NUM.match(v)
        return (float(m.group(1)) if "." in m.group(1) else int(m.group(1))) if m else None, None if m else f"not a number: {v!r}"
    if t == "bool":
        b = {"yes": True, "y": True, "true": True, "x": True, "✓": True, "no": False, "n": False, "false": False}.get(v.lower())
        return b, None if b is not None else f"not yes/no: {v!r}"
    if t == "url":
        m = URL.search(v)
        return (m.group(0) if m else v), None if m else f"no URL in {v!r}"
    if t == "enum":
        allowed = fld.get("values") or states
        return v.lower(), None if v.lower() in allowed else f"{v!r} not one of {allowed}"
    if t == "id" and fld.get("pattern") and not re.match(fld["pattern"], v):
        return v, f"id {v!r} does not match {fld['pattern']}"
    if t in DATES and not re.fullmatch(DATES[t], v):
        return v, f"not a {t}: {v!r}"
    return v, None


def table(sec: dict, start: int, body: list[str], rel: str, warn, states: dict) -> list[dict]:
    """Rows of the first table in `body`, keyed by field name, plus `_line` (1-based)."""
    i = next((k for k in range(len(body) - 1) if body[k].lstrip().startswith("|") and SEP.match(body[k + 1])), None)
    if i is None:
        warn(rel, start or None, "no table")
        return []
    head = cells(body[i])
    fields = sec["fields"]
    col = {k: head.index(f["column"]) for k, f in fields.items() if f["column"] in head}
    missing = [f["column"] for k, f in fields.items() if k not in col and "computed" not in f]
    extra = [h for h in head if h not in {f["column"] for f in fields.values()}]
    for what, cols in (("missing", missing), ("unknown, ignored", extra)):
        if cols:
            warn(rel, start + i + 1, f"{what} column(s): {', '.join(cols)}")
    rows: list[dict] = []
    for k in range(i + 2, len(body)):
        if not body[k].strip().startswith("|"):
            break
        line, c = start + k + 1, cells(body[k])
        if len(c) > len(head):
            warn(rel, line, f"row skipped: {len(c)} cells under {len(head)} columns (unescaped |?)")
            continue
        row: dict = {}
        for key, fld in fields.items():
            raw = c[col[key]] if key in col and col[key] < len(c) else ""
            row[key], problem = ([], None) if "computed" in fld else coerce(fld, raw, states.get(fld.get("lifecycle"), []))
            if problem:
                warn(rel, line, f"{key}: {problem}")
        row["_line"] = line
        rows.append(row)
    return rows


def items(body: list[str]) -> list[str]:
    out: list[str] = []
    for line in body:
        m = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if m and not line.startswith(("  ", "\t")):
            out.append(m.group(1).strip())
        elif out and line.strip() and line.startswith((" ", "\t")):
            out[-1] += " " + line.strip()
    return out


def section(repo: Path, rel: str, addr: str, sec: dict, warn, states: dict, cache: dict, sources: dict):
    shape = sec["shape"]
    empty = None if shape == "text" else []
    sources[addr] = {"path": rel, "heading": sec.get("heading"), "exists": False}
    if rel not in cache:
        p = repo / rel
        cache[rel] = p.read_text(encoding="utf-8", errors="replace").splitlines() if p.is_file() else None
        if cache[rel] is None:
            warn(rel, None, "file missing")
    if cache[rel] is None:
        return empty
    found = block(cache[rel], sec.get("heading"))
    if found is None:
        warn(rel, None, f"no '{sec['heading']}' section ({addr})")
        return empty
    sources[addr]["exists"] = True
    start, body = found
    return table(sec, start, body, rel, warn, states) if shape == "table" else items(body) if shape == "list" else "\n".join(body).strip() or None


def back_links(schema: dict, out: dict, warn) -> None:
    """Fill computed fields: the ids of the rows whose `from` field names this row."""
    def rows_at(addr: str) -> list[dict]:
        f, s = addr.split(".")[:2]
        return out[f] if isinstance(out[f], list) else out[f][s]
    for faddr, fld in pack.fields(schema).items():
        if "computed" not in fld:
            continue
        target, key = faddr.rsplit(".", 1)
        src, skey = fld["computed"]["from"].rsplit(".", 1)
        for row in rows_at(target):
            rid = row.get("id")
            row[key] = [r["id"] for r in rows_at(src) if rid is not None and r.get("id")
                        and rid in (r[skey] if isinstance(r[skey], list) else [r[skey]])]
    sec = lambda a: schema["files"][a.split(".")[0]]["sections"][a.split(".")[1]]  # noqa: E731
    for faddr, fld in pack.fields(schema).items():
        # dangling refs warn, except into tables replaced each run (yesterday's topic ids are gone by design)
        targets = [t for t in fld.get("ref", []) if sec(t).get("rows") != "replace"]
        if not targets:
            continue
        ids = {r.get("id") for t in targets for r in rows_at(t)}
        src, key = faddr.rsplit(".", 1)
        for r in rows_at(src):
            for v in r[key] if isinstance(r[key], list) else [r[key]] if r[key] else []:
                if v not in ids:
                    warn(sec(src).get("path", schema["files"][src.split(".")[0]]["path"]), r["_line"], f"{key}: {v} not found in {', '.join(targets)}")


def export(name: str, repo: Path, now: datetime | None = None) -> dict:
    schema, repo = pack.load(name), Path(repo).resolve()
    warnings: list[dict] = []
    warn = lambda rel, line, message: warnings.append({"file": rel, "line": line, "message": message})  # noqa: E731
    if name not in pack.enabled(repo):
        warn("AGENTS.md", None, f"no 'Pack: {name}' line: the repo has not turned this pack on")
    states = {k: list(lc["states"]) for k, lc in schema.get("lifecycles", {}).items()}
    cache, sources, out = {}, {}, {}
    for fkey, f in schema["files"].items():
        if f.get("many"):
            found = sorted(repo.glob(f["path"].replace("{date}", "*")))
            if not found:
                warn(f["path"], None, "no files")
            out[fkey] = [{"date": p.stem, "path": p.relative_to(repo).as_posix(), **{
                sk: section(repo, p.relative_to(repo).as_posix(), f"{fkey}.{sk}", s, warn, states, cache, {})
                for sk, s in f["sections"].items()}} for p in found]
            continue
        vals = {sk: section(repo, s.get("path", f["path"]), f"{fkey}.{sk}", s, warn, states, cache, sources) for sk, s in f["sections"].items()}
        out[fkey] = vals["rows"] if list(vals) == ["rows"] else vals
    back_links(schema, out, warn)
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"schemaVersion": EXPORT_VERSION, "pack": name, "packVersion": schema["version"], "repo": str(repo),
            "generatedAt": stamp, "warnings": warnings, **out, "sources": sources}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="pack.py <name>", description="Export a repo's pack data as one JSON document.")
    ap.add_argument("name", choices=pack.available())
    ap.add_argument("--json", action="store_true", required=True)
    ap.add_argument("--repo", type=Path, default=Path("."))
    a = ap.parse_args(argv)
    print(json.dumps(export(a.name, a.repo), indent=2, ensure_ascii=False))
    return 0
