from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
SCRIPT_PATH = REPO_ROOT / "skill" / "epic-spine" / "scripts" / "agents_block.py"

SPEC = importlib.util.spec_from_file_location("agents_block", SCRIPT_PATH)
assert SPEC and SPEC.loader
agents_block = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = agents_block
SPEC.loader.exec_module(agents_block)


class AgentsBlockTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-test-")
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def install(self, root_spine: str = "docs/spine.md") -> str:
        agents_block.install(self.repo, root_spine)
        return (self.repo / "AGENTS.md").read_text(encoding="utf-8")

    def make_spine(self, root_spine: str = "docs/spine.md") -> None:
        target = self.repo / root_spine
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Spine\n", encoding="utf-8")

    def run_check(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = agents_block.check(self.repo)
        return code, out.getvalue()

    # ------------------------------------------------------------------ #
    # install
    # ------------------------------------------------------------------ #

    def test_creates_when_missing(self) -> None:
        text = self.install()
        self.assertTrue(text.startswith("<!-- epicspine:begin"))
        self.assertIn("Root spine: docs/spine.md.", text)
        self.assertIn(agents_block.block_id(), text)
        self.assertTrue(text.rstrip().endswith("<!-- epicspine:end -->"))

    def test_appends_keeping_existing_text(self) -> None:
        agents = self.repo / "AGENTS.md"
        agents.write_text("# My Project\n\nKeep this line.\n", encoding="utf-8")
        text = self.install()
        self.assertIn("# My Project", text)
        self.assertIn("Keep this line.", text)
        self.assertIn("<!-- epicspine:begin", text)

    def test_replaces_in_place(self) -> None:
        agents = self.repo / "AGENTS.md"
        agents.write_text("# My Project\n\nold\n", encoding="utf-8")
        self.install("docs/old.md")
        text = self.install("docs/new.md")
        self.assertEqual(text.count("<!-- epicspine:begin"), 1)
        self.assertEqual(text.count("<!-- epicspine:end -->"), 1)
        self.assertIn("Root spine: docs/new.md.", text)
        self.assertNotIn("docs/old.md", text)
        self.assertIn("# My Project", text)

    def test_idempotent(self) -> None:
        first = self.install()
        second = self.install()
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # check
    # ------------------------------------------------------------------ #

    def test_check_passes(self) -> None:
        self.make_spine()
        self.install()
        code, out = self.run_check()
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_check_missing_block(self) -> None:
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("block missing", out)

    def test_check_version_differs(self) -> None:
        self.make_spine()
        text = self.install()
        text = text.replace(agents_block.block_id(), "0.0.0", 1)
        (self.repo / "AGENTS.md").write_text(text, encoding="utf-8")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("block id", out)

    def test_check_root_spine_missing(self) -> None:
        self.install("docs/absent.md")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("does not exist", out)

    def test_check_text_differs(self) -> None:
        self.make_spine()
        text = self.install()
        text = text.replace("override skill defaults", "Tampered", 1)
        (self.repo / "AGENTS.md").write_text(text, encoding="utf-8")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("differs", out)

    # ------------------------------------------------------------------ #
    # thin block + migration
    # ------------------------------------------------------------------ #

    OLD_FULL = (
        "# Proj\n\n<!-- epicspine:begin 2026.10.09 -->\n## EpicSpine — always on, every task, every agent\n"
        "Root spine: docs/spine.md. Read its Current State and Operating Learnings before acting.\n"
        "1. Bind first: first reply names role (default: delivery manager) and `Learnings in force:`.\n"
        "2. The manager never implements. Any work beyond answering a question (code, docs, research) goes to a worker.\n"
        "3. Workers: T3 delegate_task -> OpenCode instance, own worktree. Do not use native subagent tools.\n"
        "4. Integrate: verify diff and checks yourself, fast-forward main, run tests, revert on red, remove the worktree.\n"
        "5. Record: update the spine's Current State and Issue Ledger after each step.\n"
        "Precedence: user per-task instruction > this block > skill defaults.\n"
        "<!-- epicspine:end -->\n\nTail text.\n"
    )

    def test_block_is_thin_and_version_independent(self) -> None:
        text = self.install()
        block = text[text.index("<!--"):]
        self.assertLessEqual(len(block.splitlines()), 8)
        for shared in ("Bind first", "never implements", "EPICSPINE_", "file://", "Integrate:", "Stop hook"):
            self.assertNotIn(shared, block)
        for kept in ("Root spine: docs/spine.md.", "Current State and Operating Learnings", "global-block.md",
                     "Dispatch profile:", "Integration policy:", "Skill updates:", "Precedence:"):
            self.assertIn(kept, block)
        self.assertNotIn("{", block)

    def test_install_migrates_old_full_block_keeping_root_spine(self) -> None:
        self.make_spine()
        agents = self.repo / "AGENTS.md"
        agents.write_text(self.OLD_FULL, encoding="utf-8")
        self.assertEqual(self.run_check()[0], 1)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            agents_block.install(self.repo)  # no root spine given: kept from the old block
        text = agents.read_text(encoding="utf-8")
        self.assertEqual(text.count("<!-- epicspine:begin"), 1)
        self.assertIn("Root spine: docs/spine.md.", text)
        self.assertNotIn("Bind first", text)
        self.assertIn("# Proj", text)
        self.assertIn("Tail text.", text)
        self.assertEqual(self.run_check(), (0, ""))
        self.assertIn("carried over 1", out.getvalue())
        # the repo-specific worker rule survives outside the markers; stock rule 4 does not
        tail = text[text.index("<!-- epicspine:end -->"):]
        self.assertIn("- 3. Workers: T3 delegate_task -> OpenCode", tail)
        self.assertNotIn("4. Integrate", tail)
        again = agents_block.install(self.repo)
        self.assertEqual(again, 0)
        self.assertEqual(text, agents.read_text(encoding="utf-8"))

    def test_install_without_root_spine_needs_existing_block(self) -> None:
        with self.assertRaises(SystemExit):
            agents_block.install(self.repo)


if __name__ == "__main__":
    unittest.main()
