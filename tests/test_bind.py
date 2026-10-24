"""`spines.py --bind`: the compact bind view (title, Current State, Operating Learnings, open Waiting on) of an epic and its ancestors; DOD-1 keeps it lean."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SPINES = ROOT / "skill" / "epic-spine" / "scripts" / "spines.py"
STATE = "## Current State\n\nOwner: o\nStatus: active\nWaiting on: none\nNext action: {n}\n\n"


def spine(code: str, header: str, extra: str = "") -> str:
    return f"# EPIC-{code}: T{code}\n\nSpine ID: EPIC-{code}\n{header}\n\n{STATE.format(n='act-' + code)}## Operating Learnings\n\n- L-{code} | any | rule {code}\n\n{extra}## Decisions\n\nbulky decisions row\n"


def bind(repo: Path, *args: str) -> str:
    return subprocess.run([sys.executable, "-B", str(SPINES), "--repo", str(repo), "--bind", *args], capture_output=True, text=True, check=True).stdout


class BindTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "docs").mkdir()
        (self.repo / "AGENTS.md").write_text("Root spine: docs/EPIC-0-ROOT.md. Read x.\n")
        (self.repo / "docs/EPIC-0-ROOT.md").write_text(spine("0", "Spine Type: root\nRoot spine: self"))
        (self.repo / "docs/EPIC-1-LEAF.md").write_text(spine("1", "Parent spine: [root](EPIC-0-ROOT.md)", "## Waiting on\n\n- [answered E1-A1 2026-10-01 @J] old\n- [ask E1-A2 2026-10-02 @J] open one\n\n"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_default_is_root_only(self):
        out = bind(self.repo)
        self.assertIn("# EPIC-0: T0", out)
        self.assertIn("Next action: act-0", out)
        self.assertIn("L-0 | any | rule 0", out)
        self.assertNotIn("EPIC-1", out)
        self.assertNotIn("bulky decisions", out)

    def test_epic_then_ancestors_up_to_root_without_whole_files(self):
        out = bind(self.repo, "docs/EPIC-1-LEAF.md")
        self.assertLess(out.index("# EPIC-1: T1"), out.index("# EPIC-0: T0"))
        for need in ("act-1", "act-0", "L-1 | any | rule 1", "L-0 | any | rule 0", "open one"):
            self.assertIn(need, out)
        self.assertNotIn("bulky decisions", out)
        self.assertNotIn("[answered", out)
        self.assertNotIn("\n\n", out)

    def test_no_spine_says_so(self):
        empty = Path(self.tmp.name) / "none"
        empty.mkdir()
        self.assertIn("no spine found", bind(empty))

    def test_this_repo_root_bind_is_lean_and_covers_operating_learnings(self):
        out = bind(ROOT)
        self.assertIn("## Operating Learnings", out)
        self.assertIn("- L-1 |", out)
        self.assertIn("- L-20 |", out)
        self.assertLessEqual(len(out.splitlines()), 60, "root bind view is no longer lean")


if __name__ == "__main__":
    unittest.main()
