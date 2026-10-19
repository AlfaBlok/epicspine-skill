#!/usr/bin/env python3
"""Epic log helpers for spines.py / spine_new.py / session_sync.py: rollup, text views, next code, stale goals."""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

OPEN = ("draft", "ready", "active", "blocked")
CODE = re.compile(r"^(?:EPIC[- ]?|E)(\d+)\b")
STALE_DAYS = 14


def next_code(titles: list[str]) -> int:
    """Highest EPIC-<n> / `E4 ...` / `EPIC 0 ...` title code plus one."""
    return 1 + max((int(m.group(1)) for t in titles if (m := CODE.match(t.strip()))), default=0)


def rollup(own: str, kids: list[str], dod: list[dict]) -> str:
    """Derived: blocked wins; all children and criteria done: done; any progress: active; else the own status."""
    parts = kids + ["done" if d["done"] else "open" for d in dod]
    if own == "blocked" or "blocked" in kids:
        return "blocked"
    if parts and all(p == "done" for p in parts):
        return "done"
    return "active" if own == "active" or "active" in parts or "done" in parts else own or "draft"


def link_problems(child: dict, parent: dict) -> list[str]:
    """The child's header and the parent's Spine Map must agree."""
    rows = [i for i, t in parent["rows"] if t == child["path"]]
    return (["Parent spine header does not name " + parent["path"].name] if child["parent"] != parent["path"] else []) + \
        ([] if child["id"] in rows else ["Spine Map Spine ID differs"] if rows else ["not in the parent's Spine Map"])


def stale(repo: Path, nodes: list[dict], now: float | None = None) -> list[dict]:
    """Active/blocked goals whose file's last commit is 14+ days old (one git call each; untracked files are skipped)."""
    out, now = [], now or time.time()
    for n in nodes:
        if n["status"] in ("active", "blocked"):
            r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", n["path"]], cwd=repo, capture_output=True, text=True, timeout=5)
            if r.stdout.strip().isdigit() and (days := int((now - int(r.stdout)) // 86400)) >= STALE_DAYS:
                out.append({"path": n["path"], "title": n["title"], "days": days})
    return out


def active(log: dict) -> str:
    """One line per open goal: `<title> — <status> — <path>` (+ stale mark)."""
    days = {s["path"]: s["days"] for s in log["stale"]}
    return "\n".join(f"{n['title']} — {n['status']} — {n['path']}" + (f" — STALE {days[n['path']]}d" if n["path"] in days else "")
                     for n in log["nodes"] if n["status"] in OPEN)


def attention(repo: Path) -> str:
    """The background-sync line for stale goals ('' when none, no root spine, or on any error)."""
    try:
        import spines
        if spines.find_root(repo, {}) is None:
            return ""
        n = len(spines.scan(repo)["stale"])
        return f"{repo.name}: {n} goals active but untouched {STALE_DAYS}+ days (spines.py --active)" if n else ""
    except Exception:
        return ""


def render(log: dict) -> str:
    by_path = {n["path"]: n for n in log["nodes"]}
    lines: list[str] = []

    def show(path: str, depth: int) -> None:
        n, pad = by_path[path], "  " * depth
        lines.append(f"{pad}- {n['title']} ({n['path']}) {n['status'] or '?'}" + (f" -> {n['rollup_status']}" if n["rollup_status"] != n["status"] else ""))
        lines.extend(f"{pad}  [{'x' if d['done'] else ' '}] {d['id']} {d['text']}" for d in n["dod"])
        for child in n["children"]:
            show(child, depth + 1)

    if log["root"]:
        show(log["root"], 0)
    else:
        lines.append("no root spine (Root spine: none): nothing is in the tree")
    lines += [f"orphan: {o['path']} ({o['reason']})" for o in log["orphans"]]
    lines += [f"mismatch: {m['path']}: {m['problem']}" for m in log["mismatches"]]
    return "\n".join(lines)
