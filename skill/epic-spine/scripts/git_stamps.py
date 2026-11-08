"""Newest commit time of many files with one `git log` (agent_team E72-S4: the stale check ran one git per goal,
53 processes a scan on agent_team, slow on a loaded host)."""
from __future__ import annotations

import subprocess
import threading
from pathlib import Path


def last_commits(repo: Path, paths: list[str], budget: float = 10) -> dict[str, int]:
    """Committer time of each path's newest commit (`git log -1 --format=%ct -- <path>` for many paths in one process);
    a path git never saw, or one still unseen when git fails or ``budget`` seconds run out, is absent."""
    want, seen = set(paths), {}
    if not want:
        return seen
    try:
        proc = subprocess.Popen(["git", "-c", "core.quotePath=false", "log", "--format=\x01%ct", "--name-only", "--relative", "--", *want],
                                cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except (OSError, subprocess.SubprocessError):  # a loaded host must not crash the scan: these files are unknown, not stale
        return seen
    timer = threading.Timer(budget, proc.kill)
    timer.start()
    try:
        stamp = None
        for line in proc.stdout:
            line = line.rstrip("\n")
            if line.startswith("\x01"):
                stamp = int(line[1:]) if line[1:].strip().isdigit() else None
            elif line in want and line not in seen and stamp is not None:
                seen[line] = stamp
                if len(seen) == len(want):
                    break
    finally:
        timer.cancel()
        proc.kill()
        proc.stdout.close()
        proc.wait()
    return seen
