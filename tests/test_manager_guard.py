from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GUARD = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts" / "manager_guard.py"
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def sh(cwd: Path, *args: str) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, env={**os.environ, **GIT_ENV})


class ManagerGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-mg-")
        base = Path(os.path.realpath(self._tmp.name))
        self.repo, self.wt, self.home = base / "repo", base / "wt", base / "home"
        (self.repo / "docs" / "spines").mkdir(parents=True)
        (self.repo / "docs" / "spines" / "s.md").write_text("Spine ID: s\n")
        (self.repo / "app.py").write_text("x = 1\n")
        sh(base, "git", "init", "-q", "-b", "main", str(self.repo))
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", "init")
        sh(self.repo, "git", "worktree", "add", "-q", str(self.wt), "-b", "wt/x")
        self.allow = self.home / "allow"
        self.log = self.home / "guard.log"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_guard(self, tool: str = "Write", tool_input: dict | None = None, *, raw: str | None = None,
                  cwd: Path | None = None, env: dict | None = None, **extra) -> dict | None:
        cwd = cwd or self.repo
        payload = raw if raw is not None else json.dumps({
            "session_id": "s1", "cwd": str(cwd), "hook_event_name": "PreToolUse", "tool_name": tool,
            "tool_input": tool_input if tool_input is not None else {"file_path": str(cwd / "app.py"),
                                                                      "content": "x = 2\n"}, **extra})
        base_env = {k: v for k, v in os.environ.items()
                    if k not in ("CLAUDE_PROJECT_DIR", "EPICSPINE_ROLE", "EPICSPINE_MANAGER_GUARD")}
        proc = subprocess.run(
            [sys.executable, "-B", str(GUARD)], input=payload, text=True, capture_output=True, timeout=30,
            env={**base_env, "EPICSPINE_ALLOW_FILE": str(self.allow), "EPICSPINE_GUARD_LOG": str(self.log),
                 "CLAUDE_PROJECT_DIR": str(cwd), **(env or {})})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout) if proc.stdout.strip() else None

    def assertDenied(self, out: dict | None) -> str:
        self.assertIsNotNone(out)
        hso = out["hookSpecificOutput"]
        self.assertEqual((hso["hookEventName"], hso["permissionDecision"]), ("PreToolUse", "deny"))
        self.assertIn("Manager never implements — dispatch a worker (Agent tool, isolation: worktree)",
                      hso["permissionDecisionReason"])
        return hso["permissionDecisionReason"]

    def test_manager_write_denied_and_logged(self) -> None:
        reason = self.assertDenied(self.run_guard())
        self.assertIn("app.py", reason)
        self.assertIn("deny", self.log.read_text())

    def test_manager_bash_denied(self) -> None:
        self.assertDenied(self.run_guard("Bash", {"command": "gh repo create x --private"}))
        self.assertDenied(self.run_guard("Bash", {"command": "git clone git@github.com:a/b.git"}))

    def test_manager_reads_and_spine_allowed(self) -> None:
        self.assertIsNone(self.run_guard("Bash", {"command": "git status && git log -3"}))
        self.assertIsNone(self.run_guard("Edit", {"file_path": str(self.repo / "docs/spines/s.md"),
                                                  "old_string": "a", "new_string": "b"}))
        self.assertIsNone(self.run_guard("Read", {"file_path": str(self.repo / "app.py")}))
        self.assertIsNone(self.run_guard("Agent", {"prompt": "implement", "isolation": "worktree"}))

    def test_subagent_allowed(self) -> None:
        self.assertIsNone(self.run_guard(agent_id="a123", agent_type="general-purpose"))

    def test_worktree_session_is_worker(self) -> None:
        self.assertIsNone(self.run_guard(cwd=self.wt))

    def test_role_env_overrides(self) -> None:
        self.assertIsNone(self.run_guard(env={"EPICSPINE_ROLE": "worker"}))
        self.assertDenied(self.run_guard(cwd=self.wt, env={"EPICSPINE_ROLE": "manager"}))

    def test_non_git_dir_allowed(self) -> None:
        plain = self.home / "plain"
        plain.mkdir(parents=True)
        self.assertIsNone(self.run_guard(cwd=plain))

    def test_env_off(self) -> None:
        self.assertIsNone(self.run_guard(env={"EPICSPINE_MANAGER_GUARD": "off"}))

    def test_allow_once_consumed_and_logged(self) -> None:
        self.home.mkdir(exist_ok=True)
        self.allow.write_text("")
        out = self.run_guard()
        self.assertIn("override", out["systemMessage"])
        self.assertFalse(self.allow.exists())
        self.assertIn("override", self.log.read_text())
        self.assertDenied(self.run_guard())

    def test_allow_count_and_expiry(self) -> None:
        self.home.mkdir(exist_ok=True)
        self.allow.write_text("2")
        self.assertIn("systemMessage", self.run_guard())
        self.assertIn("systemMessage", self.run_guard())
        self.assertDenied(self.run_guard())
        self.allow.write_text("5")
        os.utime(self.allow, (1, 1))
        self.assertDenied(self.run_guard())
        self.assertFalse(self.allow.exists())

    def test_manager_cannot_create_marker(self) -> None:
        self.home.mkdir(exist_ok=True)
        self.allow.write_text("3")
        for cmd in ("touch ~/.agents/epicspine-allow", "echo 9 > ~/.agents/epicspine-allow"):
            self.assertIn("allow marker", self.assertDenied(self.run_guard("Bash", {"command": cmd})))
        self.assertEqual(self.allow.read_text(), "3")

    def test_repo_config(self) -> None:
        agents = self.repo / "AGENTS.md"
        agents.write_text("Manager may edit: app.py\nManager may run: `tools/gen.sh`\n")
        self.assertIsNone(self.run_guard())
        self.assertIsNone(self.run_guard("Bash", {"command": "tools/gen.sh --all"}))
        agents.write_text("Manager guard: warn\n")
        out = self.run_guard()
        self.assertIn("(warn)", out["systemMessage"])
        agents.write_text("Manager guard: off\n")
        self.assertIsNone(self.run_guard())

    def test_mcp_write_tools(self) -> None:
        self.assertDenied(self.run_guard("mcp__t3-code__t3_project_create", {"name": "x"}))
        self.assertDenied(self.run_guard("mcp__filesystem__write_file", {"path": str(self.repo / "app.py")}))
        self.assertIsNone(self.run_guard("mcp__filesystem__write_file",
                                         {"path": str(self.repo / "docs/spines/s.md")}))
        self.assertIsNone(self.run_guard("mcp__t3-code__delegate_task", {"task": "x"}))

    def test_malformed_input_fails_open(self) -> None:
        for raw in ("not json", "", "[1]", '{"tool_name": "Bash", "tool_input": 5}'):
            with self.subTest(raw=raw):
                self.assertIsNone(self.run_guard(raw=raw))


if __name__ == "__main__":
    unittest.main()
