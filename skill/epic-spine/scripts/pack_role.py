#!/usr/bin/env python3
"""Persona wake text (references/packs.md "Persona wake text"): `role_text(schema, role)` renders what one pack role may do,
from the schema alone, as the Markdown a console pastes into that persona's wake prompt. `pack.py <name> --wake-text --role R`."""
from __future__ import annotations

import pack


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
