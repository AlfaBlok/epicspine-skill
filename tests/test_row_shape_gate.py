"""agent_team E48-S205: the pre-commit gate refuses a commit that adds or changes a table row whose cell count differs
from its header (house_decision HD-S61, 24 Nov: a stray empty `| |` cell; Jordi's card press on the row was refused)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _safe_env import safe_env

GATE = Path(__file__).parent.parent / "skill" / "epic-spine" / "scripts" / "pre_commit.py"
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
HEAD = "| Issue | Owner | Title | Status | Next Action |\n|---|---|---|---|---|\n"
SPINE = "# EPIC-1: Test\n\nStatus: active\n\n## Current State\n\nStatus: active\n\n## Issue Ledger\n\n" + HEAD


class RowShapeGateTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="epicspine-rowshape-")
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        self.git("init", "-q")
        self.write(SPINE + "| E1-S1 | run_a | One | review | confirm: yes |\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "seed", "--no-verify")

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([*GIT, *args], cwd=self.repo, capture_output=True, text=True, env=safe_env())

    def write(self, text: str) -> None:
        (self.repo / "EPIC.md").write_text(text)

    def gate(self) -> subprocess.CompletedProcess:
        self.git("add", "-A")
        return subprocess.run([sys.executable, "-B", str(GATE)], cwd=self.repo, capture_output=True, text=True, env=safe_env())

    def test_a_row_with_a_stray_empty_cell_is_refused(self) -> None:
        self.write(SPINE + "| E1-S1 | run_a | One | review |  | confirm: yes |\n")
        done = self.gate()
        self.assertEqual(1, done.returncode, done.stderr)
        self.assertIn("row E1-S1 has 6 cells but its header has 5", done.stderr)

    def test_an_unescaped_pipe_in_a_new_row_is_refused(self) -> None:
        self.write(SPINE + "| E1-S1 | run_a | One | review | confirm: yes |\n| E1-S2 | run_b | A | B | ready | go |\n")
        done = self.gate()
        self.assertEqual(1, done.returncode, done.stderr)
        self.assertIn("row E1-S2 has 6 cells", done.stderr)

    def test_an_escaped_pipe_and_a_whole_row_pass(self) -> None:
        self.write(SPINE + "| E1-S1 | run_a | One | review | confirm: yes |\n| E1-S2 | run_b | A \\| B | ready | go |\n")
        done = self.gate()
        self.assertNotIn("cells but its header", done.stderr)

    def test_an_old_broken_row_the_commit_does_not_touch_never_blocks(self) -> None:
        self.write(SPINE + "| E1-S1 | run_a | One | review |  | confirm: yes |\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "broken before the gate", "--no-verify")
        self.write(SPINE + "| E1-S1 | run_a | One | review |  | confirm: yes |\n| E1-S2 | run_b | Two | ready | go |\n")
        done = self.gate()
        self.assertNotIn("cells but its header", done.stderr)


if __name__ == "__main__":
    unittest.main()
