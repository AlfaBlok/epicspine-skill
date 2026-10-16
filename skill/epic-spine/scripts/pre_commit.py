#!/usr/bin/env python3
"""Pre-commit gate (installed by ``agents_block.py install``): staged spine/ticket Markdown
must be ``validate_spine.py --trackable`` (blocks); ``--strict`` is advisory (printed, never blocks).
A staged ``.md`` is a spine if it has ``## Current State`` or ``Spine ID:``, a ticket if it has ``Ticket ID:``."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_spine as v  # noqa: E402


def main() -> int:
    staged = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], capture_output=True, text=True).stdout
    blocked = False
    for name in filter(None, staged.split("\0")):
        path = Path(name)
        if not (name.endswith(".md") and path.is_file()):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fields, sections = v.parse_fields(text), v.parse_sections(text)
        spine = "Current State" in sections or "Spine ID" in fields
        if not (spine or "Ticket ID" in fields):
            continue
        result = v.trackable(path)
        if not result["trackable"]:
            blocked = True
            print(f"epicspine: {name}: not trackable: " + "; ".join(result["missing"]), file=sys.stderr)
        if spine and v.validate_local(path).fails(strict=True):
            print(f"epicspine: {name}: --strict issues (advisory; run validate_spine.py --strict)", file=sys.stderr)
    if blocked:
        print("epicspine: commit blocked; fix the above, or bypass once with git commit --no-verify", file=sys.stderr)
    return int(blocked)


if __name__ == "__main__":
    sys.exit(main())
