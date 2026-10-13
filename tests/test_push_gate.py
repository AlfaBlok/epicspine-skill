from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

GATE = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts" / "push_gate.py"
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def sh(cwd: Path, *args: str) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, env={**os.environ, **GIT_ENV})


class PushGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-pg-")
        self.base = Path(os.path.realpath(self._tmp.name))
        self.remote, self.repo = self.base / "remote.git", self.base / "repo"
        sh(self.base, "git", "init", "-q", "--bare", "-b", "main", str(self.remote))
        sh(self.base, "git", "clone", "-q", str(self.remote), str(self.repo))
        self.commit("a.txt")
        sh(self.repo, "git", "push", "-q", "-u", "origin", "main")
        self.session = uuid.uuid4().hex

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def commit(self, name: str, repo: Path | None = None) -> None:
        repo = repo or self.repo
        (repo / name).write_text(name)
        sh(repo, "git", "add", name)
        sh(repo, "git", "commit", "-qm", name)

    def gate(self, cwd: Path | None = None, env: dict | None = None, **extra) -> dict | None:
        cwd = cwd or self.repo
        payload = {"session_id": self.session, "cwd": str(cwd), "hook_event_name": "Stop",
                   "stop_hook_active": False, **extra}
        base_env = {k: v for k, v in os.environ.items() if k not in ("EPICSPINE_ROLE", "EPICSPINE_PUSH_GATE")}
        proc = subprocess.run([sys.executable, "-B", str(GATE)], input=json.dumps(payload), text=True,
                              capture_output=True, timeout=30,
                              env={**base_env, "CLAUDE_PROJECT_DIR": str(cwd), **(env or {})})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout) if proc.stdout.strip() else None

    def assertBlocks(self, out: dict | None, *needles: str) -> None:
        self.assertIsNotNone(out)
        self.assertEqual(out.get("decision"), "block", out)
        for n in needles:
            self.assertIn(n, out["reason"])

    def test_clean_allows(self) -> None:
        self.assertIsNone(self.gate())

    def test_uncommitted_blocks_once_per_state(self) -> None:
        (self.repo / "a.txt").write_text("changed")
        (self.repo / "new.txt").write_text("new")
        self.assertBlocks(self.gate(), "2 uncommitted files, 0 unpushed commits on main", "or say why not")
        self.assertIsNone(self.gate(stop_hook_active=True))  # same state: the agent explained
        (self.repo / "more.txt").write_text("x")
        self.assertBlocks(self.gate(), "3 uncommitted files")

    def test_unpushed_commits_block(self) -> None:
        self.commit("b.txt")
        self.commit("c.txt")
        self.assertBlocks(self.gate(), "0 uncommitted files, 2 unpushed commits on main")
        sh(self.repo, "git", "push", "-q")
        self.assertIsNone(self.gate())

    def test_branch_without_upstream_counts_commits_on_no_remote(self) -> None:
        sh(self.repo, "git", "checkout", "-q", "-b", "feature")
        self.commit("f.txt")
        self.assertBlocks(self.gate(), "1 unpushed commits on feature (no upstream)")

    def test_no_remote_is_only_noted(self) -> None:
        local = self.base / "local"
        sh(self.base, "git", "init", "-q", "-b", "main", str(local))
        self.commit("x.txt", local)
        (local / "dirty.txt").write_text("d")
        out = self.gate(cwd=local)
        self.assertNotIn("decision", out)
        self.assertIn("no remote", out["systemMessage"])

    def test_worker_worktree(self) -> None:
        wt = self.base / "wt"
        sh(self.repo, "git", "worktree", "add", "-q", str(wt), "-b", "wt/task")
        self.commit("w.txt", wt)
        self.assertIsNone(self.gate(cwd=wt))  # committed, no upstream: handed to the manager
        (wt / "w2.txt").write_text("x")
        self.assertBlocks(self.gate(cwd=wt), "1 uncommitted files", "the manager integrates")

    def test_manager_sees_worker_worktrees(self) -> None:
        wt = self.base / "wt"
        sh(self.repo, "git", "worktree", "add", "-q", str(wt), "-b", "wt/task")
        self.commit("w.txt", wt)
        self.assertBlocks(self.gate(), "worker worktree", "wt/task", "1 commits not integrated")
        sh(self.repo, "git", "merge", "-q", "--ff-only", "wt/task")
        sh(self.repo, "git", "push", "-q")
        self.assertIsNone(self.gate())

    def test_background_tasks_running_allows(self) -> None:
        (self.repo / "a.txt").write_text("changed")
        self.assertIsNone(self.gate(background_tasks=[{"id": "x", "type": "subagent", "status": "running"}]))

    def test_config_and_env(self) -> None:
        (self.repo / "a.txt").write_text("changed")
        self.assertIsNone(self.gate(env={"EPICSPINE_PUSH_GATE": "off"}))
        agents = self.repo / "AGENTS.md"
        agents.write_text("Push on close: warn\n")
        out = self.gate()
        self.assertNotIn("decision", out)
        self.assertIn("uncommitted", out["systemMessage"])
        agents.write_text("Push on close: off\n")
        self.assertIsNone(self.gate())

    def test_non_repo_and_malformed(self) -> None:
        plain = self.base / "plain"
        plain.mkdir()
        self.assertIsNone(self.gate(cwd=plain))
        for raw in ("nope", "", "[1]"):
            env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
            proc = subprocess.run([sys.executable, "-B", str(GATE)], input=raw, text=True, capture_output=True,
                                  cwd=plain, env=env)
            self.assertEqual((proc.returncode, proc.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
