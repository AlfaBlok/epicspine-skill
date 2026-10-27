#!/usr/bin/env python3
"""Packs: a vertical's typed file schema a repo opts into (references/packs.md).

A pack is `packs/<name>/schema.json`: files, sections, fields, lifecycles and who may write
what. A repo opts in with one AGENTS.md line, `Pack: social` (several: `Pack: social, sales`).

  pack.py list [--repo PATH]   packs shipped (or the ones a repo has on)
  pack.py check [NAME ...]     self-consistency of each schema; exit 1 on errors
  pack.py NAME --json [--repo PATH]  one JSON document of a repo's pack data (pack_export.py)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from pathlib import Path

PACKS = Path(__file__).resolve().parents[1] / "packs"
OPT_IN = re.compile(r"^(?:EpicSpine\s+)?packs?:\s*(.+?)\s*$", re.I | re.M)
TYPES = {"id", "text", "number", "percent", "bool", "date", "datetime", "month", "url", "path", "enum", "role", "ref", "refs"}
SHAPES = {"text", "list", "table"}


def available() -> list[str]:
    return sorted(p.parent.name for p in PACKS.glob("*/schema.json"))


def load(name: str) -> dict:
    return json.loads((PACKS / name / "schema.json").read_text(encoding="utf-8"))


def enabled(repo: Path) -> list[str]:
    """Pack names a repo's AGENTS.md turns on (`Pack: social`), in order, deduplicated."""
    agents = Path(repo) / "AGENTS.md"
    if not agents.is_file():
        return []
    names: list[str] = []
    for m in OPT_IN.finditer(agents.read_text(encoding="utf-8")):
        for n in re.split(r"[,\s]+", m.group(1).strip("`")):
            if n and n.lower() not in names:
                names.append(n.lower())
    return names


def sections(schema: dict):
    """Yield (address `file.section`, section dict)."""
    for fkey, f in schema["files"].items():
        for skey, s in f["sections"].items():
            yield f"{fkey}.{skey}", s


def fields(schema: dict) -> dict[str, dict]:
    """Every field by address `file.section.field`."""
    return {f"{addr}.{k}": v for addr, s in sections(schema) for k, v in s.get("fields", {}).items()}


def field_writers(schema: dict, addr: str) -> set[str]:
    """Roles that may write one field: its own list, else the section's; lifecycle fields by transition."""
    fkey, skey, key = addr.split(".")
    s = schema["files"][fkey]["sections"][skey]
    fld = s["fields"][key]
    if "computed" in fld:
        return set()
    if "lifecycle" in fld:
        return {r for t in schema["lifecycles"][fld["lifecycle"]]["transitions"] for r in t["by"]}
    return set(fld.get("writers", s.get("writers", [])))


def writers(schema: dict) -> dict[str, set[str]]:
    """Roles that write each file (any section, field, row add or transition)."""
    out: dict[str, set[str]] = {f: set() for f in schema["files"]}
    for addr, s in sections(schema):
        who = out[addr.split(".")[0]]
        who.update(s.get("writers", []), s.get("add_rows", []))
        for key in s.get("fields", {}):
            who.update(field_writers(schema, f"{addr}.{key}"))
    return out


def reachable(lc: dict) -> set[str]:
    seen, todo = {lc["initial"]}, deque([lc["initial"]])
    while todo:
        cur = todo.popleft()
        for t in lc["transitions"]:
            if t["from"] == cur and t["to"] not in seen:
                seen.add(t["to"])
                todo.append(t["to"])
    return seen


def check(schema: dict) -> list[str]:
    """Self-consistency errors; empty means the schema is sound."""
    errs: list[str] = []
    roles = set(schema.get("roles", {}))
    secs = dict(sections(schema))
    flds = fields(schema)
    lcs = schema.get("lifecycles", {})

    def known(where: str, names) -> None:
        errs.extend(f"{where}: unknown role {r}" for r in names if r not in roles)

    known("owner", [schema.get("owner")])
    for addr, s in secs.items():
        if s.get("shape") not in SHAPES:
            errs.append(f"{addr}: shape {s.get('shape')} not one of {sorted(SHAPES)}")
        if (s.get("shape") == "table") != bool(s.get("fields")):
            errs.append(f"{addr}: fields go with shape table, and a table needs them")
        known(addr, s.get("writers", []) + s.get("add_rows", []))
        for key, fld in s.get("fields", {}).items():
            fa = f"{addr}.{key}"
            if fld.get("type") not in TYPES:
                errs.append(f"{fa}: type {fld.get('type')} not one of {sorted(TYPES)}")
            if fld.get("type") == "enum" and not (fld.get("values") or fld.get("lifecycle")):
                errs.append(f"{fa}: enum without values or lifecycle")
            if "lifecycle" in fld and lcs.get(fld["lifecycle"], {}).get("field") != fa:
                errs.append(f"{fa}: lifecycle {fld['lifecycle']} does not name this field")
            errs.extend(f"{fa}: ref to unknown section {r}" for r in fld.get("ref", []) if r not in secs)
            if fld.get("type") in ("ref", "refs") and not (fld.get("ref") or "computed" in fld):
                errs.append(f"{fa}: ref without targets")
            if "computed" in fld and fld["computed"].get("from") not in flds:
                errs.append(f"{fa}: computed from unknown field {fld['computed'].get('from')}")
            known(fa, fld.get("writers", []))
            if "computed" not in fld and not field_writers(schema, fa):
                errs.append(f"{fa}: no writer")
        if s.get("shape") != "table" and not s.get("writers"):
            errs.append(f"{addr}: no writer")
    for fkey, who in writers(schema).items():
        if not who:
            errs.append(f"file {fkey}: no writer")
    for name, lc in lcs.items():
        states = set(lc.get("states", {}))
        if lc.get("field") not in flds:
            errs.append(f"lifecycle {name}: field {lc.get('field')} unknown")
        if lc.get("initial") not in states:
            errs.append(f"lifecycle {name}: initial {lc.get('initial')} is not a state")
            continue
        kinds = set(flds.get(lc.get("kind_field"), {}).get("values", []))
        for t in lc["transitions"]:
            tag = f"lifecycle {name}: {t['from']} -> {t['to']}"
            errs.extend(f"{tag}: unknown state {x}" for x in (t["from"], t["to"]) if x not in states)
            if not t.get("by"):
                errs.append(f"{tag}: nobody may make it")
            known(tag, t.get("by", []))
            errs.extend(f"{tag}: unknown kind {k}" for k in t.get("kinds", []) if k not in kinds)
            if t.get("effect") and t["effect"] not in schema.get("effects", {}):
                errs.append(f"{tag}: unknown effect {t['effect']}")
        errs.extend(f"lifecycle {name}: {s} unreachable from {lc['initial']}" for s in sorted(states - reachable(lc)))
        path = lc.get("path", [])
        for a, b in zip(path, path[1:]):
            steps = [t for t in lc["transitions"] if (t["from"], t["to"]) == (a, b)]
            if not steps:
                errs.append(f"lifecycle {name}: path step {a} -> {b} is not a transition")
            elif schema.get("approval_gate") is False and all(set(t["by"]) <= {schema.get("owner")} for t in steps):
                errs.append(f"lifecycle {name}: path step {a} -> {b} waits on {schema.get('owner')} (approval_gate is false)")
    for rkey, rule in schema.get("rules", {}).items():
        for k in ("from", "to", "log"):
            ref = rule.get(k)
            if ref and ref not in flds and ref not in secs:
                errs.append(f"rule {rkey}: {k} {ref} unknown")
        if rule.get("to") in secs and rule.get("by") not in secs[rule["to"]].get("writers", []):
            errs.append(f"rule {rkey}: {rule.get('by')} may not write {rule['to']}")
    for ckey, c in schema.get("checks", {}).items():
        errs.extend(f"check {ckey}: unknown lifecycle {n}" for n in c.get("on", []) if n not in lcs)
        for at in c.get("at", []):
            if tuple(at.split(">")) not in {(t["from"], t["to"]) for lc in lcs.values() for t in lc["transitions"]}:
                errs.append(f"check {ckey}: at {at} is not a transition")
        if c.get("source") and c["source"] not in secs:
            errs.append(f"check {ckey}: source {c['source']} unknown")
    return errs


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] and argv[0] in available():
        return __import__("pack_export").main(argv)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--repo", type=Path)
    ck = sub.add_parser("check")
    ck.add_argument("names", nargs="*")
    a = ap.parse_args(argv)
    if a.cmd == "list":
        print("\n".join(enabled(a.repo) if a.repo else available()))
        return 0
    bad = 0
    for name in a.names or available():
        errs = check(load(name))
        print(f"{name}: " + ("ok" if not errs else f"{len(errs)} error(s)"))
        for e in errs:
            print(f"  {e}")
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
