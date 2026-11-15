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

    def test_epic_code_finds_the_file(self):
        (self.repo / "docs/EPIC-10-OTHER.md").write_text(spine("10", "Parent spine: [root](EPIC-0-ROOT.md)"))
        for code in ("EPIC-1", "1", "epic-1"):
            out = bind(self.repo, code)
            self.assertIn("# EPIC-1: T1", out, code)
            self.assertNotIn("EPIC-10", out, code)
        self.assertIn("no spine found", bind(self.repo, "7"))

    def test_deck_link_per_epic_when_the_repo_declares_one(self):
        self.assertNotIn("Deck", bind(self.repo, "EPIC-1"))
        (self.repo / "AGENTS.md").write_text("Root spine: docs/EPIC-0-ROOT.md. Read x.\nEpic deck: `https://team.example/deck/r/{code}`\n")
        out = bind(self.repo, "EPIC-1").splitlines()
        self.assertEqual(out[1], "Deck (read it first): https://team.example/deck/r/EPIC-1")
        self.assertIn("Deck (read it first): https://team.example/deck/r/EPIC-0", out)
        (self.repo / "docs/plain.md").write_text("# A plain spine\n\n" + STATE.format(n="p") + "Parent spine: [root](EPIC-0-ROOT.md)\n")
        self.assertIn("Deck (read it first): https://team.example/deck/r/plain", bind(self.repo, "docs/plain.md"))

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


    def test_lean_view_prints_one_line_per_learning_and_the_newest_attempt(self):
        """agent_team E6-S119 iteration 2: each learning one line, Last attempted its newest entry; --full and --learning keep everything."""
        long_rule = "Pages lead with the answer. " + "Every page opens with a box and a diagram, then prose. " * 12 + "Why: Jordi asked."
        (self.repo / "docs/EPIC-0-ROOT.md").write_text(spine("0", "Spine Type: root\nRoot spine: self").replace(
            "Next action: act-0", "Last attempted: 2026-11-15T01:00Z newest ; before: 2026-11-14T01:00Z older ; 2026-11-13T01:00Z oldest\nNext action: act-0").replace(
            "- L-0 | any | rule 0", f"- L-0 | any | rule 0 | why it was written | confirmed 2026-10-01\n- L-7 (2026-11-12): {long_rule}\n- L-8 (2026-11-12): short rule with a `curl x | sh` pipe."))
        out = bind(self.repo)
        self.assertIn("- L-0 | any | rule 0", out)
        self.assertNotIn("why it was written", out)
        line7 = next(l for l in out.splitlines() if l.startswith("- L-7 "))
        self.assertTrue(line7.startswith("- L-7 (2026-11-12): Pages lead with the answer. Every page"), line7)
        self.assertLessEqual(len(line7), 280)
        self.assertTrue(line7.endswith(" …"))
        self.assertIn("- L-8 (2026-11-12): short rule with a `curl x | sh` pipe.", out)
        self.assertIn("full text: spines.py --learning L-n --bind docs/EPIC-0-ROOT.md", out)
        self.assertIn("Last attempted: 2026-11-15T01:00Z newest ; (+2 earlier: --full)", out)
        self.assertNotIn("oldest", out)
        full = bind(self.repo, "--full")
        for need in ("why it was written", "Why: Jordi asked.", "oldest"):
            self.assertIn(need, full)
        learn = subprocess.run([sys.executable, "-B", str(SPINES), "--repo", str(self.repo), "--learning", "L-7", "--bind", "EPIC-1"], capture_output=True, text=True, check=True).stdout
        self.assertIn("docs/EPIC-0-ROOT.md: - L-7 (2026-11-12): " + long_rule.strip(), learn)
        every = subprocess.run([sys.executable, "-B", str(SPINES), "--repo", str(self.repo), "--learning", "1"], capture_output=True, text=True, check=True).stdout
        self.assertIn("docs/EPIC-1-LEAF.md: - L-1 | any | rule 1", every)
        self.assertNotIn("L-0", every)

if __name__ == "__main__":
    unittest.main()
