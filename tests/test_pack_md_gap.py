"""agent_team E46-S73 iteration 5: a blank line inside a pack table must not hide the rows under it."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"))
import pack_md as md  # noqa: E402

GAP = "| Id | Status |\n|---|---|\n| P-1 | scheduled |\n\n| P-2 | scheduled |\n| P-3 | posted |\n\nText after.\n"
TWO = "| Id | Status |\n|---|---|\n| P-1 | scheduled |\n\n| Other | Table |\n|---|---|\n| x | y |\n"


class BlankLineInsideTable(unittest.TestCase):
    def test_rows_under_a_blank_line_are_read(self) -> None:
        head, rows = md.table(GAP)
        self.assertEqual(["P-1", "P-2", "P-3"], [r["Id"] for r in rows])
        self.assertEqual([3], md.table_gaps(GAP))

    def test_a_second_table_after_a_blank_line_is_not_merged(self) -> None:
        self.assertEqual(["P-1"], [r["Id"] for r in md.table(TWO)[1]])
        self.assertEqual([], md.table_gaps(TWO))

    def test_text_after_the_table_ends_it(self) -> None:
        self.assertEqual(["P-1"], [r["Id"] for r in md.table("| Id |\n|---|\n| P-1 |\n\nSome text\n| P-9 |\n")[1]])


if __name__ == "__main__":
    unittest.main()
