#!/usr/bin/env python3
"""Desk intake, `pack.py <name> --wake-text`: the kinds of desk-chat message a pack defines (references/packs.md "Desk intake").

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


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="pack.py <name>", description="Print a pack's desk intake rule (wake text).")
    ap.add_argument("name", choices=pack.available())
    ap.add_argument("--wake-text", action="store_true", required=True)
    a = ap.parse_args(argv)
    schema = pack.load(a.name)
    if "intake" not in schema:
        print(f"pack {a.name} has no intake", file=sys.stderr)
        return 1
    sys.stdout.write(wake_text(schema))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
