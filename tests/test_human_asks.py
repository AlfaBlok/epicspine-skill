"""Human asks: ``## Waiting on`` parser, `waiting_on` in spines.py --json, advisory checks, goal_notes outside-repo guard (hermetic)."""
from __future__ import annotations

import datetime
import json
import re
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_epic_log as T
from test_living_tree import LivingCase

sys.path.insert(0, str(T.SCRIPTS))
import epic_log  # noqa: E402
import pre_commit  # noqa: E402
import spines  # noqa: E402

DECIDE = "- [ask: decide @Jordi since 2026-10-21 row T4] Ship E4 with one logger or two? — options: one | two — recommend: one — context: [why](docs/one-logger/notes.md#loggers)"
APPROVE = "- [ask: approve @Ana since 2026-10-20] Approve the page? — recommend: approve — context: https://example.com/page#top"
ANSWERED = "- [answered 2026-10-21 @Jordi] Ship E4 with one logger or two? — options: one | two — recommend: one — context: [why](docs/one-logger/notes.md) — answer: one"
TODAY = datetime.date(2026, 10, 22)


def waiting(*lines: str) -> str:
    return "## Waiting on\n\n" + "\n".join(lines) + "\n\n## Other\n"


class ParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-asks-")
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name).resolve()
        for name in ("docs/one-logger/notes.md", "docs/x.md", "docs/doctrine/human-asks.md"):
            (self.repo / name).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / name).write_text("x\n")

    def parse(self, *lines: str) -> list[dict]:
        return epic_log.asks(waiting(*lines), self.repo / "docs/a.md", self.repo)

    def test_every_field(self) -> None:
        self.assertEqual([{"who": "Jordi", "ask": "decide", "question": "Ship E4 with one logger or two?", "options": ["one", "two"], "recommend": "one",
                           "context": "docs/one-logger/notes.md#loggers", "since": "2026-10-21", "row": "T4", "state": "open", "answer": None}], self.parse(DECIDE))

    def test_row_is_optional_and_options_empty(self) -> None:
        ask = self.parse(APPROVE)[0]
        self.assertEqual((None, [], "approve", "Ana"), (ask["row"], ask["options"], ask["ask"], ask["who"]))

    def test_open_vs_answered(self) -> None:
        open_, answered = self.parse(DECIDE, ANSWERED)
        self.assertEqual(("open", None), (open_["state"], open_["answer"]))
        self.assertEqual(("answered", "one", "Jordi", "Ship E4 with one logger or two?"), (answered["state"], answered["answer"], answered["who"], answered["question"]))
        self.assertEqual((None, None, None), (answered["ask"], answered["since"], answered["row"]))

    def test_dash_inside_a_field_and_noise_lines(self) -> None:
        ask = self.parse("intro text", "- not an ask", "- [ask: provide @Jordi since 2026-10-21] Need the key? — context: [k](k.md) — recommend: use prod — the shared one")[0]
        self.assertEqual("use prod — the shared one", ask["recommend"])

    def test_empty_when_no_section_or_no_asks(self) -> None:
        self.assertEqual([], epic_log.asks("# t\n\n## Goal\n\nx\n", Path("/r/a.md"), Path("/r")))
        self.assertEqual([], self.parse("none"))

    def test_local_vs_external_context(self) -> None:
        with self.subTest("external kept"):
            self.assertEqual("https://example.com/page#top", self.parse(APPROVE)[0]["context"])
        with self.subTest("local resolved repo-relative"):
            repo = self.repo
            line = "- [ask: decide @J since 2026-10-21] Q? — options: a | b — recommend: a — context: [p](doctrine/human-asks.md#writing-an-ask)"
            self.assertEqual("docs/doctrine/human-asks.md#writing-an-ask", epic_log.asks(waiting(line), repo / "docs/EPIC-4-DOCTRINE-2.md", repo)[0]["context"])
            root_rel = line.replace("(doctrine/", "(docs/doctrine/")
            self.assertEqual("docs/doctrine/human-asks.md#writing-an-ask", epic_log.asks(waiting(root_rel), repo / "docs/EPIC-4-DOCTRINE-2.md", repo)[0]["context"])
        with self.subTest("bare path"):
            self.assertEqual("docs/x.md", self.parse("- [ask: provide @J since 2026-10-21] Q? — context: docs/x.md")[0]["context"])


def spine_with(ledger_status: str = "blocked", asks: str = "", status: str = "active") -> str:
    text = T.ROOT.replace("Status: active", f"Status: {status}").replace("| draft | Ticket worker | me | t | draft |", f"| T4 | Ticket worker | me | T4. t | {ledger_status} |")
    return text.replace("## Non-Goals", (f"## Waiting on\n\n{asks}\n\n" if asks else "") + "## Non-Goals")


class AdvisoryTests(unittest.TestCase):
    def issues(self, **kw) -> list[str]:
        return epic_log.ask_issues(spine_with(**kw), TODAY)

    def test_blocked_row_without_ask(self) -> None:
        found = self.issues()
        self.assertEqual(1, len(found), found)
        self.assertIn("ledger row 'T4' is blocked but no open ask names it", found[0])

    def test_open_ask_naming_the_row_clears_it(self) -> None:
        self.assertEqual([], self.issues(asks=DECIDE))

    def test_answered_or_other_row_ask_does_not_clear_it(self) -> None:
        self.assertEqual(1, len(self.issues(asks=ANSWERED)))
        self.assertEqual(1, len(self.issues(asks=DECIDE.replace("row T4", "row T9"))))

    def test_row_matches_issue_id_too(self) -> None:
        text = spine_with(asks=DECIDE.replace("row T4", "row #12")).replace("| T4 | Ticket worker", "| #12 | Ticket worker")
        self.assertEqual([], epic_log.ask_issues(text, TODAY))

    def test_unblocked_row_needs_no_ask(self) -> None:
        self.assertEqual([], self.issues(ledger_status="active"))

    def test_blocked_epic_needs_any_open_ask(self) -> None:
        self.assertEqual(["Status is blocked but no open ask is under ## Waiting on"], self.issues(ledger_status="active", status="blocked"))
        self.assertEqual([], self.issues(ledger_status="active", status="blocked", asks=APPROVE))

    def test_missing_field(self) -> None:
        cases = {"options": DECIDE.replace(" — options: one | two", ""), "recommend": DECIDE.replace(" — recommend: one", ""),
                 "context": re.sub(r" — context:.*", "", DECIDE)}
        for name, line in cases.items():
            with self.subTest(name):
                found = self.issues(asks=line)
                self.assertEqual(1, len(found), found)
                self.assertIn(f"is missing {name}", found[0])
        self.assertIn("is missing recommend", self.issues(ledger_status="active", asks=APPROVE.replace(" — recommend: approve", ""))[0])
        self.assertEqual([], self.issues(asks="- [ask: provide @J since 2026-10-21 row T4] Key? — context: docs/k.md"))
        self.assertEqual([], self.issues(ledger_status="active", asks=APPROVE))

    def test_stale_ask(self) -> None:
        old = DECIDE.replace("2026-10-21", "2026-10-14")
        self.assertEqual([], epic_log.ask_issues(spine_with(asks=DECIDE.replace("2026-10-21", "2026-10-15")), TODAY))  # exactly 7 days
        found = epic_log.ask_issues(spine_with(asks=old), TODAY)
        self.assertEqual(1, len(found))
        self.assertIn("stale ask", found[0])


class TreeCase(LivingCase):
    def setUp(self) -> None:
        super().setUp()
        self.init()
        self.assertEqual(0, self.new("docs/a.md", title="alpha").returncode)
        self.path = self.repo / "docs/a.md"
        self.text = self.path.read_text()

    def node(self) -> dict:
        return next(n for n in self.log()["nodes"] if n["path"] == "docs/a.md")

    def add_ask(self, line: str) -> None:
        self.path.write_text(self.text.replace("## Non-Goals", f"## Waiting on\n\n{line}\n\n## Non-Goals", 1))


class JsonTests(TreeCase):
    def test_empty_by_default_and_existing_fields_stay(self) -> None:
        node = self.node()
        self.assertEqual([], node["waiting_on"])
        for key in ("id", "path", "title", "parent", "status", "rollup_status", "dod", "outcome", "current_state", "children"):
            self.assertIn(key, node)

    def test_fixture_repo(self) -> None:
        self.add_ask(DECIDE + "\n" + ANSWERED)
        asks = self.node()["waiting_on"]
        self.assertEqual(["open", "answered"], [a["state"] for a in asks])
        self.assertEqual({"who", "ask", "question", "options", "recommend", "context", "since", "row", "state", "answer"}, set(asks[0]))
        self.assertEqual(["one", "two"], asks[0]["options"])
        self.assertEqual([], next(n for n in self.log()["nodes"] if n["path"] == "docs/root.md")["waiting_on"])

    def test_this_repo_epic4_has_its_open_approve_ask(self) -> None:
        repo = Path(__file__).parents[1]
        epic = next(n for n in spines.scan(repo)["nodes"] if n["path"].endswith("EPIC-4-DOCTRINE-2.md"))
        open_asks = [a for a in epic["waiting_on"] if a["state"] == "open"]
        if not open_asks:
            self.skipTest("EPIC-4's approve ask has been answered")
        self.assertEqual(("approve", "Jordi"), (open_asks[0]["ask"], open_asks[0]["who"]))


class CommitCheckTests(TreeCase):
    def test_blocked_row_warns_but_never_blocks(self) -> None:
        self.path.write_text(self.text.replace("| draft | Ticket worker |", "| T1 | Ticket worker |", 1).replace("| draft | none | none |", "| blocked | none | none |", 1))
        trackable = T.v.trackable(self.path)
        self.assertTrue(trackable["trackable"], trackable)
        self.assertIn("blocked but no open ask", " ".join(trackable["advisory"]))
        done = self.commit()
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("no open ask names it", done.stderr)

    def test_trackable_cli_reports_issues_and_exits_zero(self) -> None:
        self.add_ask(DECIDE.replace("2026-10-21", "2026-01-01"))
        cmd = [sys.executable, "-B", str(T.SCRIPTS / "validate_spine.py"), "--trackable", str(self.path)]
        done = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(0, done.returncode)
        self.assertIn("advisory: stale ask", done.stdout)

    def test_stale_ask_commits_with_warning(self) -> None:
        self.add_ask(DECIDE.replace("2026-10-21", "2026-01-01"))
        done = self.commit()
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("stale ask", done.stderr)


class GoalNotesGuardTests(TreeCase):
    def test_superseded_by_outside_the_repo_does_not_raise(self) -> None:
        outside = self.repo.parent / "outside-goal.md"
        outside.write_text("# EPIC: elsewhere\n\nSpine ID: out\n")
        self.addCleanup(outside.unlink)
        text = self.text.replace("Integration branch: main\n", "Integration branch: main\nSuperseded by: [x](../outside-goal.md)\n", 1)
        self.path.write_text(text)
        cwd = Path.cwd()
        try:
            os.chdir(self.repo)
            blocks, message = pre_commit.goal_notes("docs/a.md", text, {None: self.repo.resolve()})
        finally:
            os.chdir(cwd)
        self.assertTrue(blocks)
        self.assertIn("not an existing goal doc", message)

    def test_hook_blocks_without_traceback(self) -> None:
        self.path.write_text(self.text.replace("Integration branch: main\n", "Integration branch: main\nSuperseded by: [x](../../outside-goal.md)\n", 1))
        done = self.commit()
        self.assertNotEqual(0, done.returncode)
        self.assertNotIn("Traceback", done.stderr)
        self.assertIn("Superseded by", done.stderr)


if __name__ == "__main__":
    unittest.main()
