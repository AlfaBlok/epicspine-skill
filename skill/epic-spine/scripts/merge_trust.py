#!/usr/bin/env python3
"""Trust checks for the background sync (agent_team E59-S7, security audit H1/H2): what may land on a machine unattended.

- ``risky(path, mode)``: an added file that can run code or steer agents, which ``auto_return`` never auto-merges.
- ``first_seen``: when this machine first saw each branch tip (``<git common dir>/epicspine-seen.json``); the 2-hour wait
  counts from it, never from the committer date, which the committer sets.
- ``rewrite_guard``: refuses to fast-forward to an upstream that dropped a commit it had (a history rewrite); used by
  ``session_sync.sync_checkout`` (the skill checkout) and ``repo_sync.sync`` (every repo).
Stdlib only; never raises.
"""

from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path

from session_sync import Clock, git, out

SEEN = "epicspine-seen.json"
SCRIPT = {".py", ".pyc", ".pyw", ".pth", ".js", ".mjs", ".cjs", ".ts", ".mts", ".cts", ".jsx", ".tsx", ".sh", ".bash", ".zsh",
          ".fish", ".ksh", ".csh", ".command", ".ps1", ".psm1", ".bat", ".cmd", ".vbs", ".rb", ".pl", ".pm", ".php", ".lua", ".tcl",
          ".applescript", ".scpt", ".jar", ".exe", ".so", ".dylib", ".dll", ".wasm"}
AGENT = {"agents.md", "claude.md", "gemini.md", "claude.local.md"}
SCHEDULE_DIRS = {"cron.d", "cron.daily", "cron.hourly", "cron.weekly", "cron.monthly", "crontabs", "launchagents", "launchdaemons", "systemd"}
SCHEDULE_EXT = {".plist", ".service", ".timer", ".socket", ".path"}
BUILD = {"makefile", "gnumakefile", "justfile", "dockerfile", "containerfile", "package.json", "pyproject.toml", "setup.cfg",
         "tox.ini", "noxfile.py", "pnpm-workspace.yaml", "requirements.txt", "gemfile", "rakefile", "build.gradle", "cargo.toml"}


def risky(path: str, mode: str) -> str | None:
    """What kind of code-carrying file an added ``path`` (git ``mode``) is, or None for plain content (docs, data, images)."""
    parts = path.lower().split("/")
    name, ext = parts[-1], os.path.splitext(parts[-1])[1]
    if mode == "100755":
        return "an executable"
    if mode == "120000":
        return "a symlink"
    if mode == "160000":
        return "a submodule"
    if any(part.startswith(".") for part in parts):
        return "a dotfile or dot-directory"
    if name in AGENT:
        return "agent instructions"
    if "crontab" in name or ext in SCHEDULE_EXT or SCHEDULE_DIRS.intersection(parts[:-1]):
        return "a crontab, launchd or systemd file"
    if ext in SCRIPT:
        return "a script"
    if name in BUILD:
        return "a build or package file"
    return None


def first_seen(top: Path, clock: Clock, found: dict[str, dict], now: float) -> dict[str, float]:
    """name -> when this machine first saw the branch's current tip; updates the seen file (a new tip restarts the clock)."""
    common = out(git(["rev-parse", "--path-format=absolute", "--git-common-dir"], top, clock, 3))
    path = Path(common) / SEEN if common else None
    try:
        old = json.loads(path.read_text()) if path and path.is_file() else {}
    except (OSError, ValueError):
        old = {}
    seen: dict[str, list] = {}
    for name, info in found.items():
        tip = info.get("local") or info.get("remote")
        prior = old.get(name)
        ok = isinstance(prior, list) and len(prior) == 2 and prior[0] == tip and isinstance(prior[1], (int, float))
        seen[name] = [tip, min(float(prior[1]), now) if ok else now]
    if path and seen != old:
        try:
            tmp = path.with_name(SEEN + ".tmp")
            tmp.write_text(json.dumps(seen, sort_keys=True))
            os.replace(tmp, path)
        except OSError:
            return {}  # cannot remember: nothing counts as old enough
    return {name: when for name, (_, when) in seen.items()}


REWRITTEN = "epicspine-rewritten"


def rewrite_guard(top: Path, clock: Clock, upstream: str, before: str | None) -> str | None:
    """None when ``upstream`` still contains every earlier tip of it (``before``, the tip seen before this fetch, and any tip a
    previous run found dropped); else the dropped commit. A drop is remembered in ``<git dir>/epicspine-rewritten`` and refused
    on every run until ``upstream`` contains it again or a person removes that file (agent_team E59-S7, audit H1)."""
    rel = out(git(["rev-parse", "--git-path", REWRITTEN], top, clock, 3))
    marker = (top / rel) if rel else None
    try:
        kept = marker.read_text().split() if marker and marker.is_file() else []
    except OSError:
        kept = []
    for sha in [*kept, *([before] if before else [])]:
        proc = git(["merge-base", "--is-ancestor", sha, upstream], top, clock, 3)
        if proc is None or proc.returncode != 0:
            if marker and sha not in kept:
                with contextlib.suppress(OSError):
                    marker.write_text(sha + "\n")
            return sha
    if kept and marker:
        with contextlib.suppress(OSError):
            marker.unlink()
    return None
