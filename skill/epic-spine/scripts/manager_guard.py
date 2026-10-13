#!/usr/bin/env python3
"""Claude Code PreToolUse hook: the delivery manager never implements.

Stdin is the PreToolUse JSON. In the manager it denies state-changing Bash,
Edit/Write/MultiEdit/NotebookEdit outside spines/memory/scratch, and a short
list of state-changing MCP tools, by printing ``hookSpecificOutput`` with
``permissionDecision: deny`` (https://code.claude.com/docs/en/hooks). Policy:
guard_policy.py (+ guard_tools.py, guard_git.py, guard_lex.py).

Role: a subagent call carries ``agent_id`` -> worker, always allowed. Else
``EPICSPINE_ROLE=worker|manager`` decides; else a session whose project dir is a
linked git worktree is a worker; else manager. Outside a git repo: allowed.
Per repo (AGENTS.md lines): ``Manager guard: enforce|warn|off``,
``Manager may edit: <globs>``, ``Manager may run: <command prefixes>``.
Escape hatches, logged to ~/.agents/epicspine-guard.log:
``EPICSPINE_MANAGER_GUARD=off`` (session), or the user creates
~/.agents/epicspine-allow (empty = one action, a number N = N actions; expires
after 30 minutes). Fails open on internal errors. Stdlib only, Python 3.10+.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard_git import linked_worktree  # noqa: E402
from guard_policy import Ctx, check_command, path_ok, toplevel  # noqa: E402

MATCHER = "Bash|Edit|Write|MultiEdit|NotebookEdit|mcp__.*"
ALLOW_TTL = 1800
MARKER = "epicspine-allow"
MARKER_WHY = "only the user may create or touch the allow marker"
CONFIG = re.compile(r"^(Manager guard|Manager may edit|Manager may run|Push on close):\s*(.+?)\s*$", re.M)
MCP_WRITES = re.compile(
    r"^mcp__.*(filesystem.*__(write_file|edit_file|create_directory|move_file)|__t3_project_(create|clone|delete|update)"
    r"|github.*__(create_repository|fork_repository|push_files|create_or_update_file|delete_file|create_branch"
    r"|create_pull_request|merge_pull_request))$")
DENY = ("Manager never implements — dispatch a worker (Agent tool, isolation: worktree) for this. "
        "Blocked: {why}. The manager may read, integrate (git -C <worktree> rebase main, merge --ff-only, push, "
        "worktree remove, branch -d, run tests), edit and commit spines (docs/spines/**, files with `Spine ID:`) "
        "and memory, and serve 127.0.0.1 status pages. If the user explicitly asked you to do this yourself, "
        "ask THEM to run `touch ~/.agents/epicspine-allow` (one action; write a number for more) — never "
        "create it yourself. Repo policy: AGENTS.md `Manager may edit:` / `Manager may run:`.")


def home_file(env: str, name: str) -> Path:
    return Path(os.environ.get(env) or Path.home() / ".agents" / name).expanduser()


def log(event: str, payload: dict, detail: str) -> None:
    try:
        path = home_file("EPICSPINE_GUARD_LOG", "epicspine-guard.log")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {event} session={payload.get('session_id', '')} "
                     f"cwd={payload.get('cwd', '')} {detail[:300]!r}\n")
    except OSError:
        pass


def repo_config(root: str) -> dict[str, list[str]]:
    """``Manager guard:`` etc. from the repo's AGENTS.md; values split on commas or backticks."""
    path = Path(root) / "AGENTS.md"
    text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    out: dict[str, list[str]] = {}
    for key, val in CONFIG.findall(text):
        items = re.findall(r"`([^`]+)`", val) or [v.strip() for v in val.split(",")]
        out.setdefault(key.lower(), []).extend(i for i in items if i)
    return out


def role(payload: dict) -> str:
    if payload.get("agent_id"):
        return "worker"
    env = os.environ.get("EPICSPINE_ROLE", "").strip().lower()
    if env in ("worker", "manager"):
        return env
    project = os.environ.get("CLAUDE_PROJECT_DIR") or str(payload.get("cwd") or ".")
    return "worker" if linked_worktree(project) else "manager"


def decide(payload: dict, ctx: Ctx) -> str | None:
    tool, ti = str(payload.get("tool_name", "")), payload.get("tool_input") or {}
    if MARKER in json.dumps(ti):
        return MARKER_WHY
    if tool == "Bash":
        return check_command(str(ti.get("command", "")), ctx)
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = str(ti.get("file_path") or ti.get("notebook_path") or "")
        content = ti.get("content") if tool == "Write" else None
        return None if path and path_ok(path, ctx, content) else f"{tool} of `{path}` (not a spine or memory file)"
    if MCP_WRITES.match(tool):
        path = ti.get("path") or ti.get("destination")
        return None if isinstance(path, str) and path_ok(path, ctx) else f"`{tool}` changes state"
    return None


def consume_allow() -> bool:
    path = home_file("EPICSPINE_ALLOW_FILE", "epicspine-allow")
    try:
        if time.time() - path.stat().st_mtime > ALLOW_TTL:
            path.unlink()
            return False
        text = path.read_text(encoding="utf-8").strip()
        left = (int(text) if text.isdigit() else 1) - 1
        path.write_text(str(left)) if left > 0 else path.unlink()
        return True
    except (OSError, ValueError):
        return False


def main() -> int:
    try:
        if os.environ.get("EPICSPINE_MANAGER_GUARD", "").strip().lower() == "off":
            return 0
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict) or payload.get("hook_event_name", "PreToolUse") != "PreToolUse":
            return 0
        cwd = str(payload.get("cwd") or os.getcwd())
        root = toplevel(os.environ.get("CLAUDE_PROJECT_DIR") or cwd)
        if root is None or role(payload) == "worker":
            return 0
        cfg = repo_config(root)
        mode = (cfg.get("manager guard") or ["enforce"])[0].lower()
        if mode == "off":
            return 0
        ctx = Ctx(cwd=cwd, edit_globs=cfg.get("manager may edit", []), run_prefixes=cfg.get("manager may run", []))
        why = decide(payload, ctx)
        if why is None:
            return 0
        what = f"{payload.get('tool_name')}: {json.dumps(payload.get('tool_input'))}"
        if why != MARKER_WHY and consume_allow():
            log("override", payload, what)
            print(json.dumps({"systemMessage": f"EpicSpine manager guard: one-off user override used ({why})."}))
            return 0
        if mode == "warn":
            log("warn", payload, what)
            print(json.dumps({"systemMessage": "EpicSpine manager guard (warn): " + DENY.format(why=why)}))
            return 0
        log("deny", payload, what)
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": DENY.format(why=why)}}))
    except Exception as exc:  # noqa: BLE001 - a broken guard must not brick the session
        log("error", {}, repr(exc))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
