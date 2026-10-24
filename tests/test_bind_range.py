"""AGENTS.md names the root spine's bind range (offset/limit); it must still cover Current State through Operating Learnings."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class BindRangeTests(unittest.TestCase):
    def test_range_covers_learnings(self):
        m = re.search(r"offset (\d+) limit (\d+)", (ROOT / "AGENTS.md").read_text())
        self.assertTrue(m, "AGENTS.md lacks 'offset N limit M' bind range")
        offset, limit = int(m[1]), int(m[2])
        lines = (ROOT / "docs" / "EPIC-0-OPERATING-SYSTEM.md").read_text().split("\n")
        heads = {l: i + 1 for i, l in enumerate(lines) if l.startswith("## ")}
        self.assertLessEqual(offset, heads["## Current State"])
        self.assertGreaterEqual(offset + limit, heads["## Definition Of Done"] - 1)
        self.assertLessEqual(limit, 60, "bind range is no longer lean")


if __name__ == "__main__":
    unittest.main()
