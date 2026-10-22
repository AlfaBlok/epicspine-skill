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
        self.assertEqual([{"ref": "E4-A3", "repo": None, "code": "E4-A3", "row": "T4", "state": "unresolved"},
                          {"ref": "infra-vps/EPIC-10-A7", "repo": "infra-vps", "code": "EPIC-10-A7", "row": "3", "state": "unresolved"}],
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
                self.assertEqual([{"ref": "E4-A1", "repo": None, "code": "E4-A1", "row": "T4", "state": state}], self.waits("- [waits on E4-A1 row T4] g"))

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


if __name__ == "__main__":
    unittest.main()
