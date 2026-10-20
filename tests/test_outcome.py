"""Outcome before close (trackable rule + spines.py --json `outcome`) and the `current_state` JSON field (hermetic)."""
from __future__ import annotations

import re
import subprocess
import sys
import unittest

import test_epic_log as T

sys.path.insert(0, str(T.SCRIPTS))
import spine_fix  # noqa: E402

OUTCOME = """## Outcome

Verdict: partially accomplished
Outcome: Shipped the parser; the console card is follow-up.
Closed: 2026-10-20 by EPIC-4 delivery manager (run 7)
Risk: none

| Done means | Evidence |
|---|---|
| E1-1 First criterion | [PR #31](https://github.com/o/r/pull/31), 0891cbb |
| E1-2 Second criterion | none |

"""


class OutcomeCase(T.EpicLogCase):
    def setUp(self) -> None:
        super().setUp()
        self.assertEqual(0, self.new("docs/a.md", title="alpha").returncode)
        self.path = self.repo / "docs/a.md"
        self.text = self.path.read_text()

    def edit(self, status: str = "draft", outcome: str = "", extra: str = "") -> dict:
        text = self.text.replace("Status: draft", f"Status: {status}")
        text = text.replace("Integration branch: main\n", f"Integration branch: main\n{extra}", 1)
        self.path.write_text(text.replace("## Current State", outcome + "## Current State", 1))
        return T.v.trackable(self.path)

    def node(self) -> dict:
        return next(n for n in self.log()["nodes"] if n["path"] == "docs/a.md")


class TrackableOutcomeTests(OutcomeCase):
    def test_open_spine_needs_no_outcome(self) -> None:
        for status in ("draft", "ready", "active", "blocked"):
            self.assertTrue(self.edit(status)["trackable"], status)

    def test_closed_spine_needs_a_filled_outcome(self) -> None:
        for status in ("done", "done — shipped"):
            result = self.edit(status)
            self.assertFalse(result["trackable"], status)
            self.assertIn("write `## Outcome`", result["missing"][0])
        self.assertTrue(self.edit("done", OUTCOME)["trackable"])

    def test_superseded_by_close_needs_an_outcome(self) -> None:
        extra = "Superseded by: [root](root.md)\n"
        self.assertFalse(self.edit("done", extra=extra)["trackable"])
        self.assertTrue(self.edit("done", OUTCOME.replace("partially accomplished", "superseded"), extra)["trackable"])

    def test_partial_outcome_is_not_enough(self) -> None:
        for bad in (OUTCOME.replace("partially accomplished", "mostly"), OUTCOME.replace("Verdict: partially accomplished\n", ""),
                    OUTCOME.replace("Outcome: Shipped the parser; the console card is follow-up.", "Outcome: <one sentence>"),
                    "## Outcome\n\nVerdict: accomplished\n\n"):
            self.assertFalse(self.edit("done", bad)["trackable"], bad)

    def test_fix_never_invents_an_outcome(self) -> None:
        self.edit("done")
        spine_fix.main([self.path])
        self.assertNotIn("## Outcome", self.path.read_text())
        self.assertFalse(T.v.trackable(self.path)["trackable"])

    def test_cli_exit_code_blocks(self) -> None:
        self.edit("done")
        cmd = [sys.executable, "-B", str(T.SCRIPTS / "validate_spine.py"), "--trackable", str(self.path)]
        self.assertEqual(1, subprocess.run(cmd, capture_output=True, text=True).returncode)


class JsonOutcomeTests(OutcomeCase):
    def test_absent_is_null(self) -> None:
        self.assertIsNone(self.node()["outcome"])

    def test_present_follows_the_console_contract(self) -> None:
        self.edit("done", OUTCOME)
        self.assertEqual({
            "verdict": "partially accomplished", "sentence": "Shipped the parser; the console card is follow-up.",
            "evidence": [{"done_means": "E1-1 First criterion", "links": ["https://github.com/o/r/pull/31", "0891cbb"]},
                         {"done_means": "E1-2 Second criterion", "links": []}],
            "risk": None, "closed_at": "2026-10-20", "closed_by": "EPIC-4 delivery manager (run 7)"}, self.node()["outcome"])

    def test_partial_gives_nulls(self) -> None:
        self.edit("done", "## Outcome\n\nVerdict: accomplished\nClosed: 2026-10-20\nRisk: watch the cache\n\n")
        self.assertEqual({"verdict": "accomplished", "sentence": None, "evidence": [], "risk": "watch the cache",
                          "closed_at": "2026-10-20", "closed_by": None}, self.node()["outcome"])
        self.edit("done", "## Outcome\n\nVerdict: <accomplished | partially accomplished>\n\n")
        self.assertEqual(None, self.node()["outcome"]["verdict"])


class CurrentStateJsonTests(OutcomeCase):
    def test_present(self) -> None:
        body = "Status: active\nLast attempted: ran the suite\nResult: 3 failures\nWaiting on: none\nNext action: fix them\nVerified at: 2026-10-20"
        self.path.write_text(re.sub(r"(?s)## Current State\n.*?\n## ", f"## Current State\n\n{body}\n\n## ", self.text, count=1))
        state = self.node()["current_state"]
        self.assertEqual(["status", "last_attempted", "result", "evidence", "waiting_on", "next_action", "verified_at"], list(state))
        self.assertEqual(("active", "ran the suite", "3 failures", "none", "fix them", "2026-10-20"),
                         (state["status"], state["last_attempted"], state["result"], state["waiting_on"], state["next_action"], state["verified_at"]))
        self.assertEqual(state["status"], self.node()["status"])

    def test_partial_labels_are_null(self) -> None:
        self.path.write_text(re.sub(r"(?s)## Current State\n.*?\n## ", "## Current State\n\nStatus: ready\nResult:\n\n## ", self.text, count=1))
        state = self.node()["current_state"]
        self.assertEqual("ready", state["status"])
        self.assertTrue(all(v is None for k, v in state.items() if k != "status"), state)

    def test_absent_section_is_null(self) -> None:
        self.path.write_text(self.text.replace("## Current State", "## State of play", 1))
        self.assertIsNone(self.node()["current_state"])


if __name__ == "__main__":
    unittest.main()
