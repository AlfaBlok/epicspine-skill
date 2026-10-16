"""Hermetic stand-ins for ``crontab`` and ``launchctl`` (never touch the real ones). State lives under ``<bin>/state``."""
from __future__ import annotations

import os
import stat
from pathlib import Path
from unittest import mock

CRONTAB = """#!/bin/sh
state="$(dirname "$0")/state"; mkdir -p "$state"
echo "crontab $*" >> "$state/calls"
case "$1" in
  -l) [ -f "$state/fail-read" ] && { echo "crontab: cannot read" >&2; exit 1; }
      if [ -f "$state/crontab" ]; then cat "$state/crontab"; else echo "no crontab for tester" >&2; exit 1; fi ;;
  -) [ -f "$state/fail-write" ] && exit 1; cat > "$state/crontab" ;;
  *) exit 2 ;;
esac
"""
LAUNCHCTL = """#!/bin/sh
state="$(dirname "$0")/state"; mkdir -p "$state"
echo "launchctl $*" >> "$state/calls"
case "$1" in
  print) [ -f "$state/loaded" ] ;;
  bootstrap) [ -f "$state/no-bootstrap" ] && exit 5; : > "$state/loaded" ;;
  load) : > "$state/loaded" ;;
  bootout|unload) rm -f "$state/loaded" ;;
esac
"""


def install(bin_dir: Path, cron: str | None = None) -> mock._patch_dict:
    """Write fake crontab/launchctl into ``bin_dir`` and return a started PATH patch (caller stops it)."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    for name, text in (("crontab", CRONTAB), ("launchctl", LAUNCHCTL)):
        path = bin_dir / name
        path.write_text(text)
        path.chmod(path.stat().st_mode | stat.S_IEXEC)
    if cron is not None:
        (bin_dir / "state").mkdir(exist_ok=True)
        (bin_dir / "state" / "crontab").write_text(cron)
    patch = mock.patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"})
    patch.start()
    return patch


def calls(bin_dir: Path) -> list[str]:
    path = bin_dir / "state" / "calls"
    return path.read_text().splitlines() if path.exists() else []


def crontab_text(bin_dir: Path) -> str:
    path = bin_dir / "state" / "crontab"
    return path.read_text() if path.exists() else ""
