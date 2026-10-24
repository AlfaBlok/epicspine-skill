"""Standing spines (references/standing-spines.md, scripts/standing.py): positive and negative fixture per rule; legacy spines untouched."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from test_validate_spine import validate_spine as v

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"))
import spines  # noqa: E402
BASE = (Path(__file__).parents[1] / "examples/EPIC-COMPACT-EXAMPLE.md").read_text()
TARGETS = "## Targets\n\n| Target | Per | Measure |\n|---|---|---|\n| 3 posts published | week | count in the publishing log |\n\n"
SCORE = "Scoreboard: 2026-W43: 2/3 posts published\n"


def standing(*, targets: str = TARGETS, score: str = SCORE, status: str = "active", dod: bool = False, kind: str = "Spine kind: standing\n") -> str:
    text = BASE.replace("Spine profile: compact\n", f"Spine profile: compact\n{kind}").replace("Status: ready", f"Status: {status}\n{score}".rstrip("\n"))
    text = text.replace("## Mission", f"{targets}## Mission")
    if not dod:
        text = text.split("## Definition Of Done")[0] + "## Issue Ledger" + text.split("## Issue Ledger")[1]
    return text


class StandingTests(unittest.TestCase):
    def doc(self, text: str):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EPIC-1-S.md"
            path.write_text(text)
            return v.validate_local(path), v.trackable(path)

    def errors(self, text: str) -> list[str]:
        return self.doc(text)[0].errors

    def test_valid_standing_spine_passes_strict_without_outcome_or_done_means(self):
        doc, track = self.doc(standing())
        self.assertEqual((doc.errors, doc.fails(strict=True)), ([], False))
        self.assertTrue(track["trackable"], track["missing"])

    def test_done_means_still_accepted_when_present(self):
        self.assertEqual(self.errors(standing(dod=True)), [])

    def test_non_standing_spine_still_needs_done_means(self):
        self.assertIn("missing section: Definition Of Done", self.errors(standing(kind="")))

    def test_targets_section_required(self):
        self.assertIn("standing spine missing section: ## Targets (| Target | Per | Measure |)", self.errors(standing(targets="")))

    def test_targets_columns_required_and_header_parenthetical_ignored(self):
        self.assertIn("Targets table missing column: Measure", self.errors(standing(targets=TARGETS.replace("| Measure ", "").replace("|---|---|---|", "|---|---|").replace("| count in the publishing log ", ""))))
        self.assertEqual(self.errors(standing(targets=TARGETS.replace("| Per |", "| Per (period) |"))), [])

    def test_targets_need_a_row_and_no_empty_cell(self):
        empty = "## Targets\n\n| Target | Per | Measure |\n|---|---|---|\n\n"
        self.assertIn("Targets has no rows: one target per period", self.errors(standing(targets=empty)))
        self.assertIn("Targets row 1 has empty Per", self.errors(standing(targets=TARGETS.replace("| week |", "|  |"))))

    def test_scoreboard_required(self):
        self.assertIn("standing spine Current State missing `Scoreboard:` (target vs actual this period)", self.errors(standing(score="")))
        self.assertTrue(self.errors(standing(score="Scoreboard: <target vs actual>\n")))

    def test_done_status_rejected(self):
        for word in ("done", "closed"):
            self.assertTrue(any("never closes" in e for e in self.errors(standing(status=word))), word)
        self.assertEqual(self.errors(standing(status="deferred")), [])

    def test_miss_is_an_ordinary_ledger_row(self):
        row = "| draft | Ticket worker | example-worker | Missed W42: 1/3 posts | draft | none | b | main | log | 2026-10-24 | catch up |\n"
        text = standing().replace("| draft | Ticket worker | example-worker | Review CLI explanation | draft | none | codex/example | 6f63d378 | Synthetic draft only | 2026-09-06 | Read acceptance command |\n", row)
        self.assertEqual(self.errors(text), [])

    def test_legacy_spine_with_targets_section_untouched(self):
        legacy = BASE.replace("## Mission", TARGETS + "## Mission")
        self.assertEqual(self.errors(legacy), [])

    def test_spines_json_marks_standing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".git").mkdir()
            (repo / "docs").mkdir()
            (repo / "AGENTS.md").write_text("Root spine: docs/EPIC-1-S.md\n")
            root = standing().replace("Spine ID: synthetic-compact-example\n", "Spine ID: s\nSpine Type: root\nRoot spine: self\nParent spine: none\n")
            (repo / "docs/EPIC-1-S.md").write_text(root)
            out = spines.scan(repo)
        node = next(n for n in out["nodes"] if n["path"] == "docs/EPIC-1-S.md")
        self.assertEqual(node["standing"], {"targets": [{"target": "3 posts published", "per": "week", "measure": "count in the publishing log"}], "scoreboard": "2026-W43: 2/3 posts published"})


if __name__ == "__main__":
    unittest.main()
