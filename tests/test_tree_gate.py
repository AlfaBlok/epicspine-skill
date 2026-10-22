"""EPIC-4 step 18: a test that commits through the pre-commit hook runs the gate of the checkout under test, from a linked
worktree too, while a normally installed hook still points at the main checkout."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _safe_env import safe_env

TESTS = Path(__file__).parent
SKILL = TESTS.parent / "skill" / "epic-spine"
MARKER = "WORKTREE-GATE-MARKER"
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
INSTALL_TREE = ("import sys, pathlib; sys.path[:0] = sys.argv[2:4]; import agents_block, tree_gate; "
                "tree_gate.install(agents_block, pathlib.Path(sys.argv[1]), 'none')")  # fresh process: agents_block of the worktree


class TreeGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-treegate-")
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.main, self.wt, self.target = root / "main", root / "wt", root / "target"
        shutil.copytree(SKILL, self.main / "skill/epic-spine", ignore=shutil.ignore_patterns("__pycache__"))
        self.git(self.main, "init", "-q")
        self.git(self.main, "add", "-A")
        self.git(self.main, "commit", "-qm", "main")
        self.git(self.main, "worktree", "add", "-q", "-b", "b", str(self.wt))
        gate = self.wt / "skill/epic-spine/scripts/pre_commit.py"  # the branch's gate differs from main's
        gate.write_text(f"import sys\nprint({MARKER!r}, file=sys.stderr)\nsys.exit(1)\n")
        self.target.mkdir()
        self.git(self.target, "init", "-q")

    def git(self, cwd: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([*GIT, *args], cwd=cwd, capture_output=True, text=True, env=safe_env())

    def commit(self) -> subprocess.CompletedProcess:
        (self.target / "a.md").write_text("# a\n")
        self.git(self.target, "add", "-A")
        return self.git(self.target, "commit", "-m", "x")

    def install(self, *cmd: str) -> None:
        done = subprocess.run([sys.executable, "-B", *cmd], capture_output=True, text=True, env=safe_env())
        self.assertEqual(0, done.returncode, done.stderr)

    def test_worktree_gate_runs_only_through_tree_gate(self) -> None:
        scripts = self.wt / "skill/epic-spine/scripts"
        self.install(str(scripts / "agents_block.py"), "install", "--repo", str(self.target), "--root-spine", "none")
        self.assertIn(str(self.main / "skill/epic-spine"), (self.target / ".git/hooks/pre-commit").read_text())  # real installs stay durable
        plain = self.commit()
        self.assertEqual(0, plain.returncode, plain.stderr)  # main's gate ran, not the worktree's
        self.assertNotIn(MARKER, plain.stderr)
        self.git(self.target, "reset", "-q", "--hard")
        self.install("-c", INSTALL_TREE, str(self.target), str(TESTS), str(scripts))
        self.assertIn(str(self.wt / "skill/epic-spine"), (self.target / ".git/hooks/pre-commit").read_text())
        blocked = self.commit()
        self.assertNotEqual(0, blocked.returncode)
        self.assertIn(MARKER, blocked.stderr)  # the worktree's own gate ran
