#!/usr/bin/env python3
"""Claude Code Stop hook: every session ends with work committed and pushed.

Checks the session's repo (``CLAUDE_PROJECT_DIR``, else ``cwd``) when a final
answer is produced. Manager: uncommitted files, and commits not on the upstream
(or on no remote when there is no upstream), plus EpicSpine worker worktrees
(``.claude/worktrees/*`` or branch ``wt/*``) with uncommitted or unintegrated
work. Worker (linked worktree or ``EPICSPINE_ROLE=worker``): uncommitted files,
and unpushed commits only if the branch has an upstream (the manager integrates).
A repo with no remote is only noted (``systemMessage``), never blocked.

Blocks (``{"decision": "block"}``) once per distinct state per session, so "say
why not" ends the loop and an unchanged dirty repo does not nag every turn. No
check while background tasks are running. Per repo: AGENTS.md ``Push on close:
enforce|warn|off``; ``EPICSPINE_PUSH_GATE=off`` disables. Fails open.
Stdlib only, Python 3.10+.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ in an installed skill
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard_policy import toplevel  # noqa: E402
from manager_guard import repo_config, role  # noqa: E402


def git(path: str, *args: str) -> list[str]:
    proc = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True, timeout=15)
    return proc.stdout.splitlines() if proc.returncode == 0 else []


def state(path: str) -> dict:
    lines = git(path, "status", "--porcelain=2", "--branch")
    head = {k: v for k, _, v in (ln[2:].partition(" ") for ln in lines if ln.startswith("# "))}
    dirty = sum(1 for ln in lines if ln and not ln.startswith("#"))
    upstream, remotes = head.get("branch.upstream"), git(path, "remote")
    ahead = 0
    if upstream:
        ahead = int((re.search(r"\+(\d+)", head.get("branch.ab", "")) or [0, 0])[1])
    elif remotes and head.get("branch.oid", "(initial)") != "(initial)":
        ahead = int((git(path, "rev-list", "--count", "HEAD", "--not", "--remotes") or ["0"])[0])
    return {"branch": head.get("branch.head", "?"), "dirty": dirty, "ahead": ahead,
            "upstream": upstream, "remote": bool(remotes)}


def worker_worktrees(root: str) -> list[tuple[str, str]]:
    out, path = [], None
    for ln in git(root, "worktree", "list", "--porcelain"):
        if ln.startswith("worktree "):
            path = ln[9:]
        elif ln.startswith("branch refs/heads/") and path and os.path.realpath(path) != os.path.realpath(root):
            branch = ln[18:]
            if branch.startswith("wt/") or "/.claude/worktrees/" in path + "/":
                out.append((path, branch))
    return out


def findings(root: str, worker: bool) -> tuple[list[str], list[str]]:
    """(problems that block, notes that only inform)."""
    s, problems, notes = state(root), [], []
    unpushed = s["ahead"] if (s["upstream"] or (s["remote"] and not worker)) else 0
    if not s["remote"]:
        if s["dirty"]:
            notes.append(f"{root}: no remote; {s['dirty']} uncommitted files on {s['branch']}")
    elif s["dirty"] or unpushed:
        where = "" if s["upstream"] else " (no upstream)"
        problems.append(f"{s['dirty']} uncommitted files, {unpushed} unpushed commits on {s['branch']}{where}")
    if not worker:
        for path, branch in worker_worktrees(root):
            dirty = state(path)["dirty"]
            ahead = int((git(root, "rev-list", "--count", f"refs/heads/{branch}", "--not", "HEAD", "--remotes")
                         or ["0"])[0])
            if dirty or ahead:
                problems.append(f"worker worktree {path} ({branch}): {dirty} uncommitted files, "
                                f"{ahead} commits not integrated")
    return problems, notes


def memo(session: str) -> Path:
    safe = re.sub(r"[^\w.-]", "_", session or "nosession")[:80]
    return Path(tempfile.gettempdir()) / "epicspine-push-gate" / f"{safe}.fp"


def main() -> int:
    try:
        if os.environ.get("EPICSPINE_PUSH_GATE", "").strip().lower() == "off":
            return 0
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict) or payload.get("agent_id"):
            return 0
        if any(isinstance(t, dict) and t.get("status") == "running" for t in payload.get("background_tasks") or []):
            return 0
        root = toplevel(os.environ.get("CLAUDE_PROJECT_DIR") or str(payload.get("cwd") or os.getcwd()))
        if root is None:
            return 0
        mode = (repo_config(root).get("push on close") or ["enforce"])[0].lower()
        if mode == "off":
            return 0
        worker = role(payload) == "worker"
        problems, notes = findings(root, worker)
        if not problems and not notes:
            return 0
        fp = hashlib.sha256(json.dumps([problems, notes]).encode()).hexdigest()
        path = memo(str(payload.get("session_id", "")))
        if path.is_file() and path.read_text() == fp:
            return 0
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fp)
        if not problems:
            print(json.dumps({"systemMessage": "EpicSpine push-on-close: " + "; ".join(notes)}))
            return 0
        todo = ("commit your work in this worktree (the manager integrates and pushes)" if worker else
                "commit and push (dispatch a worker for non-spine changes; integrate or discard worker worktrees)")
        reason = f"EpicSpine push-on-close: {'; '.join(problems + notes)} — {todo}, or say why not, before closing."
        print(json.dumps({"systemMessage": reason} if mode == "warn" else {"decision": "block", "reason": reason}))
    except Exception:  # noqa: BLE001 - fail open
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
