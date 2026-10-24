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
DO = ("- [ask E4-A3: do @Jordi since 2026-10-21 row T4] Patch the archiver for 1 h so the cutover (T4) can run? — steps: [runbook](docs/x.md#run) (vps1, user root) — unblocks: T4; each day waiting loses a day of ticks"
      " — recommend: do it tonight — effort: ~10 min — context: [why](docs/one-logger/notes.md#archiver)")
DECIDE2 = "- [ask E4-A1: decide @Jordi since 2026-10-21 row T4] Ship E4 with one logger or two? — options: one | two — recommend: one — unblocks: T4 — context: [why](docs/one-logger/notes.md#loggers)"
APPROVE2 = "- [ask E4-A2: approve @Ana since 2026-10-20] Approve the page? — recommend: approve — unblocks: T5 — context: https://example.com/page#top"
ANSWERED_V2 = "- [answered E4-A3 2026-10-22 @Jordi] Patch the archiver? — answer: done"
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
        self.assertEqual([{"code": None, "who": "Jordi", "ask": "decide", "question": "Ship E4 with one logger or two?", "steps": None, "options": ["one", "two"], "recommend": "one",
                           "unblocks": None, "effort": None, "context": "docs/one-logger/notes.md#loggers", "since": "2026-10-21", "row": "T4", "state": "open", "answer": None, "superseded_by": None}], self.parse(DECIDE))

    def test_v2_do_ask_with_every_new_field(self) -> None:
        self.assertEqual({"code": "E4-A3", "who": "Jordi", "ask": "do", "question": "Patch the archiver for 1 h so the cutover (T4) can run?", "steps": "docs/x.md#run (vps1, user root)",
                          "options": [], "recommend": "do it tonight", "unblocks": "T4; each day waiting loses a day of ticks", "effort": "~10 min",
                          "context": "docs/one-logger/notes.md#archiver", "since": "2026-10-21", "row": "T4", "state": "open", "answer": None, "superseded_by": None}, self.parse(DO)[0])

    def test_steps_inline_commands_are_kept(self) -> None:
        line = DO.replace("[runbook](docs/x.md#run) (vps1, user root)", "`sudo systemctl restart archiver` on vps1")
        self.assertEqual("`sudo systemctl restart archiver` on vps1", self.parse(line)[0]["steps"])

    def test_code_shapes(self) -> None:
        for code in ("EPIC-4-A1", "E4-A12", "M2-A3", "poly-A1"):
            with self.subTest(code):
                self.assertEqual(code, self.parse(DO.replace("E4-A3", code))[0]["code"])
        for bad in ("E4-3", "A3", "E4-Ax"):
            with self.subTest(bad):
                self.assertEqual([], self.parse(DO.replace("E4-A3", bad)))

    def test_v1_lines_have_null_code_and_new_fields(self) -> None:
        for ask in self.parse(DECIDE, APPROVE, ANSWERED):
            self.assertEqual((None, None, None, None), (ask["code"], ask["steps"], ask["unblocks"], ask["effort"]))

    def test_answered_with_code(self) -> None:
        ask = self.parse(ANSWERED_V2)[0]
        self.assertEqual(("answered", "E4-A3", "Jordi", "done"), (ask["state"], ask["code"], ask["who"], ask["answer"]))
        self.assertEqual((None, None, None), (ask["ask"], ask["since"], ask["row"]))

    def test_provide_do_types_accepted_and_unknown_type_kept(self) -> None:
        self.assertEqual("do", self.parse(DO)[0]["ask"])
        self.assertEqual(("fix", "open"), tuple(self.parse(DO.replace(": do @", ": fix @"))[0][k] for k in ("ask", "state")))  # read, and the checks advise

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
        self.assertEqual([], self.issues(asks=DECIDE2))

    def test_answered_or_other_row_ask_does_not_clear_it(self) -> None:
        self.assertEqual(1, len(self.issues(asks=ANSWERED)))
        self.assertEqual(1, len(self.issues(asks=DECIDE2.replace("row T4", "row T9"))))

    def test_row_matches_issue_id_too(self) -> None:
        text = spine_with(asks=DECIDE2.replace("row T4", "row #12")).replace("| T4 | Ticket worker", "| #12 | Ticket worker")
        self.assertEqual([], epic_log.ask_issues(text, TODAY))

    def test_unblocked_row_needs_no_ask(self) -> None:
        self.assertEqual([], self.issues(ledger_status="active"))

    def test_blocked_epic_needs_any_open_ask(self) -> None:
        self.assertEqual(["Status is blocked but no open ask is under ## Waiting on"], self.issues(ledger_status="active", status="blocked"))
        self.assertEqual([], self.issues(ledger_status="active", status="blocked", asks=APPROVE2))

    def test_missing_field(self) -> None:
        cases = {"options": DECIDE2.replace(" — options: one | two", ""), "recommend": DECIDE2.replace(" — recommend: one", ""),
                 "context": re.sub(r" — context:.*", "", DECIDE2)}
        for name, line in cases.items():
            with self.subTest(name):
                found = self.issues(asks=line)
                self.assertEqual(1, len(found), found)
                self.assertIn(f"is missing {name}", found[0])
        self.assertIn("is missing recommend", self.issues(ledger_status="active", asks=APPROVE2.replace(" — recommend: approve", ""))[0])
        self.assertEqual([], self.issues(asks="- [ask E4-A5: provide @J since 2026-10-21 row T4] Key? — unblocks: T4 — context: docs/k.md"))
        self.assertEqual([], self.issues(ledger_status="active", asks=APPROVE2))

    def test_waiting_row_needs_an_ask_like_blocked(self) -> None:
        found = self.issues(ledger_status="waiting")
        self.assertEqual(1, len(found), found)
        self.assertIn("ledger row 'T4' is waiting but no open ask names it", found[0])
        self.assertEqual([], self.issues(ledger_status="waiting", asks=DO))
        self.assertEqual(["Status is waiting but no open ask is under ## Waiting on"], self.issues(ledger_status="active", status="waiting"))

    def test_v2_required_fields(self) -> None:
        cases = {"steps": re.sub(r" — steps: .*?(?= — unblocks)", "", DO), "unblocks": re.sub(r" — unblocks: .*?(?= — recommend)", "", DO),
                 "recommend": DO.replace(" — recommend: do it tonight", ""), "context": re.sub(r" — context:.*", "", DO)}
        for name, line in cases.items():
            with self.subTest(name):
                found = self.issues(asks=line)
                self.assertEqual(1, len(found), found)
                self.assertIn(f"ask E4-A3 is missing {name}", found[0])
        self.assertEqual([], self.issues(asks=DO))  # effort is optional
        self.assertEqual([], self.issues(asks=DO.replace(" — effort: ~10 min", "")))

    def test_unblocks_required_for_every_type(self) -> None:
        v2 = "- [ask E4-A1: approve @Ana since 2026-10-21 row T4] Approve the page? — recommend: approve — context: docs/x.md"
        self.assertEqual(["ask E4-A1 is missing unblocks"], self.issues(asks=v2))
        self.assertEqual([], self.issues(asks=v2 + " — unblocks: T4"))
        self.assertEqual(["ask E4-A1 is missing unblocks"], self.issues(asks=v2.replace("approve @Ana", "provide @Ana").replace(" — recommend: approve", "")))

    def test_ask_without_code_is_flagged(self) -> None:
        found = self.issues(asks=DECIDE.replace(" — context", " — unblocks: T4 — context"))
        self.assertEqual(1, len(found), found)
        self.assertIn("has no code", found[0])

    def test_over_three_open_asks(self) -> None:
        four = [DO.replace("E4-A3", f"E4-A{n}") for n in range(1, 5)]
        self.assertEqual([], self.issues(asks="\n".join(four[:3])))
        found = self.issues(asks="\n".join(four))
        self.assertEqual(1, len(found), found)
        self.assertIn("4 open asks", found[0])
        self.assertEqual([], [i for i in self.issues(asks="\n".join(four[:3] + [ANSWERED_V2.replace("E4-A3", "E4-A9")])) if "open asks" in i])

    def test_duplicate_code_among_open_asks(self) -> None:
        found = self.issues(asks=DO + "\n" + DO.replace("row T4", "row T9"))
        self.assertEqual(1, len([i for i in found if "duplicate ask code E4-A3" in i]), found)
        self.assertEqual([], [i for i in self.issues(asks=DO + "\n" + DO.replace("E4-A3", "E4-A30")) if "duplicate" in i])

    def test_open_ask_whose_code_is_in_a_decisions_row(self) -> None:
        with_row = spine_with(asks=DO).replace("| accepted | c |", "| accepted | E4-A3 patch |")
        self.assertTrue([i for i in epic_log.ask_issues(with_row, TODAY) if "duplicate ask code E4-A3" in i])
        self.assertEqual([], [i for i in epic_log.ask_issues(with_row.replace("E4-A3 patch", "E4-A31 patch"), TODAY) if "duplicate" in i])
        answered_only = with_row.replace(DO, ANSWERED_V2)
        self.assertEqual([], [i for i in epic_log.ask_issues(answered_only, TODAY) if "duplicate" in i])  # an answered line may sit beside its Decisions row

    def test_next_row_naming_a_human_needs_an_ask(self) -> None:
        def spine(status: str, needs: str = "", owner: str = "me", asks: str = "") -> str:
            text = spine_with(ledger_status=status, asks=asks).replace("| me | T4. t |", f"| {owner} | T4. t |")
            if needs:
                text = text.replace("| Issue |", "| Needs | Issue |", 1).replace("|---|", "|---|---|", 1).replace("| T4 |", f"| {needs} | T4 |", 1)
            return text
        flag = lambda **kw: [i for i in epic_log.ask_issues(spine(**kw), TODAY) if "is next" in i]  # noqa: E731
        with self.subTest("Needs is a bare name"):
            self.assertEqual(1, len(flag(status="ready", needs="Jordi")))
            self.assertEqual(1, len(flag(status="active", needs="@Jordi")))
        with self.subTest("an open ask naming the row clears it"):
            self.assertEqual([], flag(status="ready", needs="Jordi", asks=DO))
        with self.subTest("Owner is the who of an ask elsewhere"):
            self.assertEqual(1, len(flag(status="ready", owner="Jordi", asks=DO.replace("row T4", "row T9"))))
            self.assertEqual([], flag(status="ready", owner="Jordi"))  # no ask names a Jordi: stay quiet
        with self.subTest("low noise"):
            self.assertEqual([], flag(status="ready", needs="none"))
            self.assertEqual([], flag(status="ready", needs="the doctrine page"))
            self.assertEqual([], flag(status="draft", needs="Jordi"))
            self.assertEqual([], flag(status="ready", owner="worker (Sonnet 5.5)"))

    def test_stale_ask(self) -> None:
        old = DECIDE2.replace("2026-10-21", "2026-10-14")
        self.assertEqual([], epic_log.ask_issues(spine_with(asks=DECIDE2.replace("2026-10-21", "2026-10-15")), TODAY))  # exactly 7 days
        found = epic_log.ask_issues(spine_with(asks=old), TODAY)
        self.assertEqual(1, len(found))
        self.assertIn("stale ask", found[0])


class WritingTests(unittest.TestCase):
    """Ask-writing advisories (human-asks.md "Writing an ask"; agent_team root L-13/L-14), never blocking."""
    def issues(self, line: str) -> list[str]:
        return epic_log.ask_issues(spine_with(asks=line), TODAY)

    def test_a_plain_ask_is_clean(self) -> None:
        self.assertEqual([], self.issues(DECIDE2))

    def test_future_triggers(self) -> None:
        for q in ("Scan the QR when pinged?", "Provide the keys before Wave 2?", "Approve the redirect later?",
                  "Approve the redirect once the site is up?"):
            found = self.issues(DECIDE2.replace("Ship E4 with one logger or two?", q))
            self.assertEqual(1, len(found), q)
            self.assertIn("future trigger", found[0])
        found = self.issues(DECIDE2.replace("recommend: one", "recommend: one, scan later"))
        self.assertIn("future trigger ('later')", found[0])
        self.assertEqual([], self.issues(DECIDE2.replace("Ship E4", "Ship E4 at once")))  # `once` alone is not a trigger

    def test_numbered_parts(self) -> None:
        found = self.issues(DECIDE2.replace("Ship E4 with one logger or two?", "(1) Ship E4 with one logger? (2) Rotate the keys?"))
        self.assertEqual(1, len(found))
        self.assertIn("several numbered parts", found[0])

    def test_long_question_sentence(self) -> None:
        long = "Ship E4 with one logger " + "and the archiver " * 12 + "or two?"
        found = self.issues(DECIDE2.replace("Ship E4 with one logger or two?", long))
        self.assertEqual(1, len(found))
        self.assertIn("question sentence over 200 chars", found[0])
        short = "Ship E4 with one logger or two? " + "It keeps the archiver simple. " * 6
        self.assertEqual([], self.issues(DECIDE2.replace("Ship E4 with one logger or two?", short.strip())))

    def test_answered_asks_are_not_checked(self) -> None:
        found = self.issues("- [answered E4-A1 2026-10-22 @Jordi] Scan the QR when pinged? (1) a (2) b — answer: yes")
        self.assertFalse([i for i in found if "future trigger" in i or "numbered parts" in i])

    def test_trigger_word_is_case_insensitive(self) -> None:
        self.assertIn("future trigger", " ".join(self.issues(DECIDE2.replace("Ship E4", "Later, ship E4"))))


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
        self.add_ask(DECIDE + "\n" + ANSWERED_V2)
        asks = self.node()["waiting_on"]
        self.assertEqual(["open", "answered"], [a["state"] for a in asks])
        self.assertEqual({"code", "who", "ask", "question", "steps", "options", "recommend", "unblocks", "effort", "context", "since", "row", "state", "answer", "superseded_by"}, set(asks[0]))
        self.assertEqual(["one", "two"], asks[0]["options"])
        self.assertEqual([], next(n for n in self.log()["nodes"] if n["path"] == "docs/root.md")["waiting_on"])

    def test_this_repo_epic4_has_its_open_approve_ask(self) -> None:
        repo = Path(__file__).parents[1]
        epic = next(n for n in spines.scan(repo)["nodes"] if n["path"].endswith("EPIC-4-DOCTRINE-2.md"))
        open_asks = [a for a in epic["waiting_on"] if a["state"] == "open"]
        if not open_asks:
            self.skipTest("EPIC-4's approve ask has been answered")
        self.assertEqual(("approve", "Jordi"), (open_asks[0]["ask"], open_asks[0]["who"]))
        self.assertRegex(open_asks[0]["code"], r"^EPIC-4-A\d+$")
        self.assertTrue(open_asks[0]["unblocks"])
        self.assertEqual([], T.v.trackable(repo / epic["path"])["advisory"])


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
