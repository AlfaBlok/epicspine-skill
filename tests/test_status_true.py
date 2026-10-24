"""Status-true advisories (EPIC-6, scripts/status_true.py): positive and negative fixture per rule; strict promotes them."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test_validate_spine import validate_spine as validator

BASE = (Path(__file__).parents[1] / "examples/EPIC-COMPACT-EXAMPLE.md").read_text()
CODED = "- [ask EX-A1: decide @Jordi since 2026-10-24 row T1] Ship it? — options: yes | no — recommend: yes"
ROW = "| draft | Ticket worker | example-worker | Review CLI explanation | draft |"
JORDI_ROW = "| draft | Ticket worker | Jordi | T1 Approve the page | ready |"


def spine(waiting: str = "", *, status: str = "ready", said: str = "none", box: str = "- [ ]", row: str = ROW) -> str:
    text = BASE.replace("Status: ready", f"Status: {status}").replace("Waiting on: none", f"Waiting on: {said}").replace("- [ ] DOD-1", f"{box} DOD-1").replace(ROW, row)
    return text.replace("## Issue Ledger", f"## Waiting on\n\n{waiting}\n\n## Issue Ledger") if waiting else text


class StatusTrueTests(unittest.TestCase):
    def check(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "epic.md"
            path.write_text(text)
            doc = validator.validate_local(path)
        found = [w for w in doc.warnings if w.startswith("status-true")]
        self.assertEqual(bool(found), doc.fails(strict=True) and not doc.errors, doc.errors)  # warnings promoted by --strict only
        return found

    def test_clean_fixture_raises_nothing(self):
        self.assertEqual([], self.check(spine()))

    def test_free_text_waiting_on_line_naming_jordi(self):
        self.assertEqual(1, len(self.check(spine("- Waiting on Jordi to approve the page"))))
        self.assertEqual([], self.check(spine(CODED, said="Jordi: EX-A1")))
        self.assertEqual([], self.check(spine("- none")))

    def test_current_state_waiting_on_naming_jordi_without_a_code(self):
        self.assertEqual(1, len(self.check(spine(said="Jordi: approve the page"))))

    def test_open_ledger_row_owned_by_jordi_needs_a_coded_ask(self):
        self.assertEqual(1, len(self.check(spine(row=JORDI_ROW))))
        self.assertEqual([], self.check(spine(CODED, said="Jordi: EX-A1", row=JORDI_ROW)))
        self.assertEqual([], self.check(spine(row=JORDI_ROW.replace("| ready |", "| done |"))))

    def test_status_done_with_unticked_done_means(self):
        self.assertEqual(1, len(self.check(spine(status="done"))))
        self.assertEqual([], self.check(spine(status="done", box="- [x]")))

    def test_done_row_citing_an_unticked_criterion(self):
        row = ROW.replace("Review CLI explanation | draft", "Review CLI explanation (DOD-1) | done")
        self.assertEqual(1, len(self.check(spine(row=row))))
        self.assertEqual([], self.check(spine(box="- [x]", row=row)))

    def test_nothing_open_beside_an_open_coded_ask(self):
        found = self.check(spine(CODED, said="nobody"))
        self.assertEqual(1, len(found))
        self.assertIn("EX-A1", found[0])
        self.assertEqual([], self.check(spine(CODED, said="Jordi: EX-A1")))
        self.assertEqual([], self.check(spine(CODED.replace("[ask EX-A1: decide @Jordi since 2026-10-24 row T1]", "[answered EX-A1 2026-10-24 @Jordi]"), said="nobody")))


if __name__ == "__main__":
    unittest.main()
