"""D19 (EPIC-4 step 20): `waits on` references, `· done` answers, search-before-asking checks (hermetic: temp repos, a sibling checkout)."""
from __future__ import annotations

import datetime
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import test_epic_log as T
from test_human_asks import ANSWERED_V2, APPROVE2, DECIDE2, TODAY, TreeCase, spine_with

sys.path.insert(0, str(T.SCRIPTS))
import epic_log  # noqa: E402

REF = "- [waits on E4-A3 row T4] Needs the archiver patch first"
DONE = ANSWERED_V2 + " · done 2026-10-22 abc1234"


def refs(*lines: str) -> list[dict]:
    return epic_log.waits("## Waiting on\n\n" + "\n".join(lines) + "\n\n## Other\n")


class ParseTests(unittest.TestCase):
    def test_same_repo_and_cross_repo_forms(self) -> None:
        self.assertEqual([{"ref": "E4-A3", "repo": None, "code": "E4-A3", "row": "T4", "state": "unresolved", "via": "waits_on"},
                          {"ref": "infra-vps/EPIC-10-A7", "repo": "infra-vps", "code": "EPIC-10-A7", "row": "3", "state": "unresolved", "via": "waits_on"}],
                         refs(REF, "- [waits on infra-vps/EPIC-10-A7 row 3] The VPS key"))

    def test_row_is_optional_and_asks_are_not_references(self) -> None:
        self.assertEqual([None], [r["row"] for r in refs("- [waits on EPIC-4-A2] gloss")])
        self.assertEqual([], refs(DECIDE2, ANSWERED_V2, "- [waits on nothing] x"))
        self.assertEqual([], epic_log.asks("## Waiting on\n\n" + REF + "\n", Path("-"), Path("-")))

    def test_done_suffix_gives_state_done_and_is_stripped_from_the_answer(self) -> None:
        got = epic_log.asks("## Waiting on\n\n" + DONE + "\n", Path("-"), Path("-"))[0]
        self.assertEqual(("E4-A3", "done", "done"), (got["code"], got["state"], got["answer"]))
        for line in (ANSWERED_V2 + " · done 2026-10-22", ANSWERED_V2 + " · done 2026-10-22 abc1234"):
            self.assertEqual("done", epic_log.asks("## Waiting on\n\n" + line + "\n", Path("-"), Path("-"))[0]["state"])
        self.assertEqual("answered", epic_log.asks("## Waiting on\n\n" + ANSWERED_V2 + "\n", Path("-"), Path("-"))[0]["state"])


# Real lines (infra-vps EPIC-10:138, EPIC-2:71 and :67, EPIC-10:130, poly-maker E4 before fe93a1cb, EPIC-0:25), shortened.
SUPERSEDED = "- [superseded EPIC-10-A8 2026-10-22 by EPIC-10-A9] The Dokploy upgrade broke zenod's CI deploy step; merge the fix? — recommend: yes, merge it"
DONE_NOTE = "- [answered EPIC-2-A9 2026-10-23 @delivery-manager · done 2026-10-23 8091316 superseded by EPIC-2-A12] S5 row 9 — answer: decided by the manager"
DONE_IN_TAG = "- [answered EPIC-10-A1 2026-10-22 @Jordi · done 2026-10-22 567f58b] Approve the redeploys? — answer: yes to 1 to 7 now · done 2026-10-22 567f58b"
ANSWER_IN_TAG = '- [answered EPIC-2-A13 2026-10-23 @Jordi: "force reboot immediately", run now] Run S14 Step 1 tonight'


def state_says(waiting_on: str, asks: str = "") -> str:
    return f"# EPIC-4: t\n\n## Current State\n\nStatus: active\nWaiting on: {waiting_on}\n\n## Waiting on\n\n{asks}\n\n## Other\n"


class StatesTests(unittest.TestCase):
    def parse(self, line: str, problems: list | None = None) -> dict:
        return epic_log.asks("## Waiting on\n\n" + line + "\n", Path("-"), Path("-"), problems)[0]

    def test_superseded_ask(self) -> None:
        got = self.parse(SUPERSEDED)
        self.assertEqual(("EPIC-10-A8", "superseded", "EPIC-10-A9", None), (got["code"], got["state"], got["superseded_by"], got["who"]))
        self.assertEqual("yes, merge it", got["recommend"])
        self.assertEqual("infra-vps/EPIC-10-A9", self.parse(SUPERSEDED.replace("by EPIC", "by infra-vps/EPIC"))["superseded_by"])

    def test_done_marker_in_the_tag_with_a_trailing_note(self) -> None:
        problems: list[str] = []
        got = self.parse(DONE_NOTE, problems)
        self.assertEqual(("EPIC-2-A9", "delivery-manager", "done", "EPIC-2-A12", "decided by the manager"), tuple(got[k] for k in ("code", "who", "state", "superseded_by", "answer")))
        got = self.parse(DONE_IN_TAG, problems)
        self.assertEqual(("EPIC-10-A1", "Jordi", "done", "yes to 1 to 7 now"), tuple(got[k] for k in ("code", "who", "state", "answer")))
        self.assertEqual("done", self.parse(DONE + " — note: rolled out by run_1")["state"])
        self.assertEqual([], problems)

    def test_waiting_on_codes_are_references_and_nobody_is_none(self) -> None:
        got = epic_log.waits(state_says("Jordi: E4-A8 (podcek), E4-A9 (tables), E4-A7 (traces), infra-vps/EPIC-10-A7"))
        self.assertEqual([("E4-A8", None, "waiting_on"), ("E4-A9", None, "waiting_on"), ("E4-A7", None, "waiting_on"), ("infra-vps/EPIC-10-A7", "infra-vps", "waiting_on")],
                         [(r["ref"], r["repo"], r["via"]) for r in got])
        self.assertEqual(["EPIC-3-A1"], [r["code"] for r in epic_log.waits(state_says("Jordi: EPIC-3-A1 (root spines for the six rootless repos; asked in EPIC-3)"))])
        for none in ("nobody (Jordi: none open). Workers: A9 table export + drop; T10 default flip", "none (closed, EPIC-10-A9 done)", "Nothing"):
            self.assertEqual([], epic_log.waits(state_says(none)), none)
        both = epic_log.waits(state_says("Jordi: E4-A3", "- [waits on E4-A3 row T4] g"))
        self.assertEqual([("E4-A3", "waits_on")], [(r["ref"], r["via"]) for r in both])  # one reference per code

    def test_unreadable_forms_are_advised_with_the_canonical_form(self) -> None:
        text = state_says("Jordi — pick reuse or rebuild", "\n".join(["- A9-7 Name the Chrome profile", "- [closed E4-A2] gone", "- [ask EPIC-13-A1: run @Jordi since 2026-10-23] Run the audit — unblocks: S1 — context: x.md",
                                                                       ANSWER_IN_TAG, SUPERSEDED, DONE_NOTE, "- none", "  - a sub-bullet"]))
        found = epic_log.ask_issues(text, TODAY)
        self.assertEqual(2, sum("is not a form the tools read: write `[ask <code>" in f for f in found), found)
        self.assertTrue(any("type 'run' is not one of decide | approve | provide | do" in f for f in found), found)
        self.assertTrue(any("EPIC-2-A13: tag carries '\"force reboot immediately\", run now'" in f for f in found), found)
        self.assertTrue(any("names a human but no ask code" in f for f in found), found)
        self.assertEqual(6, len(found), found)  # + EPIC-13-A1 is missing recommend
        self.assertEqual([], epic_log.ask_issues(state_says("nobody (manager merge)") , TODAY))
        self.assertEqual([], epic_log.ask_issues(state_says("Jordi: EPIC-3-A1 (asked in EPIC-3)"), TODAY))


class ResolveTests(TreeCase):
    def setUp(self) -> None:
        super().setUp()
        self.sibling = self.repo.parent / "sib-repo-for-asks"
        shutil.rmtree(self.sibling, ignore_errors=True)
        (self.sibling / "docs").mkdir(parents=True)
        (self.sibling / "AGENTS.md").write_text("Root spine: docs/root.md.\n")
        (self.sibling / "docs/root.md").write_text(T.ROOT.replace("## Non-Goals", "## Waiting on\n\n" + APPROVE2.replace("E4-A2", "INFRA-A7") + "\n\n## Non-Goals"))
        self.addCleanup(shutil.rmtree, self.sibling, True)

    def waits(self, *lines: str) -> list[dict]:
        self.add_ask("\n".join(lines))
        return self.node()["waits_on"]

    def test_same_repo_state_follows_the_target_ask(self) -> None:
        root = self.repo / "docs/root.md"
        for line, state in ((DECIDE2, "open"), (ANSWERED_V2.replace("E4-A3", "E4-A1"), "answered"), (DONE.replace("E4-A3", "E4-A1"), "done")):
            with self.subTest(state):
                root.write_text(T.ROOT.replace("## Non-Goals", f"## Waiting on\n\n{line}\n\n## Non-Goals"))
                self.assertEqual([{"ref": "E4-A1", "repo": None, "code": "E4-A1", "row": "T4", "state": state, "via": "waits_on"}], self.waits("- [waits on E4-A1 row T4] g"))

    def test_same_repo_unresolved_and_own_name_qualifier(self) -> None:
        self.assertEqual("unresolved", self.waits("- [waits on E4-A9 row T4] g")[0]["state"])
        (self.repo / "docs/root.md").write_text(T.ROOT.replace("## Non-Goals", "## Waiting on\n\n" + DECIDE2 + "\n\n## Non-Goals"))
        self.assertEqual("open", self.waits(f"- [waits on {self.repo.name}/E4-A1 row T4] g")[0]["state"])

    def test_cleaned_up_ask_with_a_decisions_row_is_done(self) -> None:
        root = self.repo / "docs/root.md"
        root.write_text(T.ROOT.replace("## Decisions", "## Decisions\n\n| 2026-10-21 | decide | E4-A5: ship one logger | one | none |\n"))
        self.assertEqual("done", self.waits("- [waits on E4-A5 row T4] g")[0]["state"])

    def test_cross_repo_resolves_through_a_sibling_checkout(self) -> None:
        got = self.waits("- [waits on sib-repo-for-asks/INFRA-A7 row 3] g", "- [waits on sib-repo-for-asks/INFRA-A8] g", "- [waits on nowhere-repo/X-A1] g")
        self.assertEqual(["open", "unresolved", "unresolved"], [w["state"] for w in got])
        self.assertEqual(("sib-repo-for-asks/INFRA-A7", "sib-repo-for-asks", "INFRA-A7", "3"), tuple(got[0][k] for k in ("ref", "repo", "code", "row")))

    def test_superseded_and_waiting_on_references_resolve(self) -> None:
        (self.repo / "docs/root.md").write_text(T.ROOT.replace("## Non-Goals", "## Waiting on\n\n" + SUPERSEDED.replace("EPIC-10-A8", "E4-A1") + "\n\n## Non-Goals"))
        self.add_ask("- [waits on E4-A1 row T4] g")
        self.path.write_text(self.path.read_text().replace("Waiting on: none", "Waiting on: Jordi: E4-A1, sib-repo-for-asks/INFRA-A7, sib-repo-for-asks/INFRA-A9", 1))
        got = self.node()["waits_on"]
        self.assertEqual([("E4-A1", "superseded", "waits_on"), ("sib-repo-for-asks/INFRA-A7", "open", "waiting_on"), ("sib-repo-for-asks/INFRA-A9", "unresolved", "waiting_on")],
                         [(r["ref"], r["state"], r["via"]) for r in got])

    def test_waiting_on_is_unchanged_by_references(self) -> None:
        self.waits(REF)
        self.assertEqual([], self.node()["waiting_on"])


class AdvisoryTests(TreeCase):
    def test_reference_satisfies_a_blocked_row_and_blocked_epic(self) -> None:
        self.assertEqual(1, len(epic_log.ask_issues(spine_with(), TODAY)))
        self.assertEqual([], epic_log.ask_issues(spine_with(asks="- [waits on E4-A3 row T4] g"), TODAY))
        self.assertEqual(1, len(epic_log.ask_issues(spine_with(asks="- [waits on E4-A3 row T9] g"), TODAY)))
        self.assertEqual([], epic_log.ask_issues(spine_with(ledger_status="active", status="blocked", asks="- [waits on E4-A3] g"), TODAY))

    def test_references_never_count_toward_three_open_asks_and_never_go_stale(self) -> None:
        four = "\n".join(f"- [waits on E4-A{n} row T4] g" for n in range(1, 5))
        self.assertEqual([], epic_log.ask_issues(spine_with(asks=four), TODAY))
        self.assertEqual([], epic_log.ask_issues(spine_with(asks=four), TODAY + datetime.timedelta(days=400)))

    def test_done_lines_are_never_open_stale_or_surplus(self) -> None:
        old = "\n".join(DONE.replace("E4-A3", f"E4-A{n}").replace("2026-10-22 @", "2026-01-01 @") for n in range(1, 6))
        found = epic_log.ask_issues(spine_with(ledger_status="active", asks=old), TODAY)
        self.assertEqual([], found)
        undone = "## Waiting on\n\n" + old.replace(" · done 2026-10-22 abc1234", "") + "\n"
        self.assertEqual("answered", epic_log.asks(undone, Path("-"), Path("-"))[0]["state"])  # without `· done` the same lines are the owner's action items

    def test_unknown_same_repo_code_warns_known_and_cross_repo_do_not(self) -> None:
        root = self.repo / "docs/root.md"
        root.write_text(T.ROOT.replace("## Non-Goals", "## Waiting on\n\n" + DECIDE2 + "\n\n## Non-Goals"))
        self.add_ask("- [waits on E4-A1 row T4] ok\n- [waits on E4-A9 row T4] typo\n- [waits on infra-vps/EPIC-10-A7 row T4] elsewhere")
        found = epic_log.ask_issues(self.path.read_text(), TODAY, self.repo)
        self.assertEqual(1, len(found), found)
        self.assertIn("waits on E4-A9: no ask with that code exists in this repo", found[0])
        self.assertEqual([], epic_log.ask_issues(self.path.read_text(), TODAY), "no repo given: no existence check")

    def test_commit_check_warns_without_blocking(self) -> None:
        self.add_ask("- [waits on E4-A9 row T4] typo")
        done = self.commit()
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("waits on E4-A9: no ask with that code exists", done.stderr)
        self.assertTrue(T.v.trackable(self.path)["trackable"])
        self.assertIn("waits on E4-A9", " ".join(T.v.trackable(self.path)["advisory"]))

    def test_commit_check_advises_unreadable_lines_without_blocking(self) -> None:
        self.add_ask("- [closed E4-A2 2026-10-22] gone")
        done = self.commit()
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("'- [closed E4-A2 2026-10-22] gone' is not a form the tools read: write `[ask <code>", done.stderr)


if __name__ == "__main__":
    unittest.main()
