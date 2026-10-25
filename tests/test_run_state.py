"""Runnable epics (EPIC-7, scripts/run_state.py): the Status table, has_children, the --active suffix and the advisory warnings."""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from test_epic_log import EpicLogCase
from test_status_true import BASE
from test_validate_spine import validate_spine as validator

TABLE = {"draft": ("planning", False), "ready": ("ready", True), "active": ("running", True), "blocked": ("running", True),
         "deferred": ("parked", False), "review": ("finished", False), "done": ("finished", False), "superseded": ("finished", False),
         "": ("planning", False), "paused": ("planning", False)}
ROW = "| draft | Ticket worker | example-worker | Review CLI explanation | draft |"


class RunStateTests(EpicLogCase):
    def child(self, status: str, path: str = "docs/E4-one-logger.md", parent: str = "docs/root.md") -> dict:
        self.new(path, parent)
        text = self.repo / path
        text.write_text(re.sub(r"(?m)^Status: .*$", f"Status: {status}", text.read_text()))
        return {n["path"]: n for n in self.log()["nodes"]}

    def test_every_status_row_of_the_table(self) -> None:
        for status, (state, runnable) in TABLE.items():
            with self.subTest(status=status):
                node = self.child(status)["docs/E4-one-logger.md"]
                self.assertEqual((state, runnable), (node["run_state"], node["runnable"]))

    def test_doctrine_table_and_closing_line_say_review(self) -> None:
        text = (Path(__file__).parents[1] / "skill/epic-spine/references/spine-model.md").read_text()
        self.assertIn("| review | finished | no (", text)
        self.assertRegex(text, r"Outcome written without `Verdict:`.*`Status: review`.*verdict → `done`")

    def test_run_state_reads_the_own_status_not_the_rollup(self) -> None:
        nodes = self.child("active")
        self.assertEqual(("running", True), (nodes["docs/root.md"]["run_state"], nodes["docs/root.md"]["runnable"]))
        self.assertEqual("done", self.child("done")["docs/E4-one-logger.md"]["status"])

    def test_has_children_is_true_only_for_a_child_not_finished(self) -> None:
        for status, expected in (("ready", True), ("draft", True), ("active", True), ("deferred", True), ("blocked", True), ("done", False), ("review", False), ("superseded", False)):
            with self.subTest(child=status):
                nodes = self.child(status)
                self.assertEqual(expected, nodes["docs/root.md"]["has_children"])
                self.assertFalse(nodes["docs/E4-one-logger.md"]["has_children"])

    def test_a_scaffolded_epic_is_draft_and_never_auto_queued(self) -> None:
        self.new()
        self.assertIn("Status: draft", (self.repo / "docs/E4-one-logger.md").read_text())
        self.assertIn("| draft |", (self.repo / "docs/root.md").read_text().split("## Spine Map")[1])
        node = {n["path"]: n for n in self.log()["nodes"]}["docs/E4-one-logger.md"]
        self.assertEqual(("planning", False), (node["run_state"], node["runnable"]))

    def test_a_childless_spine_has_no_children(self) -> None:
        self.assertFalse(self.log()["nodes"][0]["has_children"])

    def test_has_children_counts_any_unfinished_child(self) -> None:
        self.new("docs/E5-a.md")
        self.new("docs/E6-b.md")
        b = self.repo / "docs/E6-b.md"
        for name in ("E5-a", "E6-b"):
            p = self.repo / f"docs/{name}.md"
            p.write_text(re.sub(r"(?m)^Status: .*$", "Status: done", p.read_text()))
        self.assertFalse(self.log()["nodes"][0]["has_children"])
        b.write_text(b.read_text().replace("Status: done", "Status: active"))
        self.assertTrue(self.log()["nodes"][0]["has_children"])

    def test_active_text_carries_the_run_state(self) -> None:
        self.new()
        lines = self.run_script("spines.py", "--active").stdout.splitlines()
        self.assertIn("— running, has children", lines[0])
        self.assertTrue(lines[1].endswith("— planning (not runnable)"), lines[1])  # a scaffold is draft, never auto-queued


class RunStateAdvisoryTests(unittest.TestCase):
    def found(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "epic.md"
            path.write_text(text)
            doc = validator.validate_local(path)
        found = [w for w in doc.warnings if w.startswith("run-state")]
        self.assertFalse(doc.fails(strict=True) and found and not doc.errors, "advisory only: --strict never fails on it")
        return found

    def spine(self, status: str, attempted: str = "Drafted the synthetic CLI explanation.", row_status: str = "draft") -> str:
        return BASE.replace("Status: ready", f"Status: {status}").replace("Last attempted: Drafted the synthetic CLI explanation.", f"Last attempted: {attempted}").replace(ROW, ROW.replace("| draft |", f"| {row_status} |"))

    def test_active_with_no_start_recorded(self) -> None:
        self.assertEqual(1, len(self.found(self.spine("active", "scaffolded with spine_new.py on 2026-10-24"))))
        self.assertEqual(1, len(self.found(self.spine("active", ""))))
        self.assertEqual([], self.found(self.spine("active", "persona e7-worker started 2026-10-24")))
        self.assertEqual([], self.found(self.spine("ready", "scaffolded with spine_new.py on 2026-10-24")))

    def test_draft_epic_with_active_ledger_rows(self) -> None:
        self.assertEqual(1, len(self.found(self.spine("draft", row_status="active"))))
        self.assertEqual([], self.found(self.spine("draft")))
        self.assertEqual([], self.found(self.spine("active", row_status="active")))


if __name__ == "__main__":
    unittest.main()
