"""E90-S3 (agent_team EPIC-90, many humans): the `## People` list and the ask tag's approve by, aware, escalated by,
awaits and approved parts read back right; a spine with two humans (hermetic: no repo needed)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import test_epic_log as T

sys.path.insert(0, str(T.SCRIPTS))
import ask_refs  # noqa: E402
import people  # noqa: E402

ROOT = """# agent_team

## People

- @Jordi : owner · area: all · alerts: WhatsApp, daily summary 08:00 Mexico City
- @Marta : expert · area: books, tax filings · alerts: email, browser 09:00 to 18:00 Madrid
- @Leo : analyst · area: books · escalates to: @Marta after 24 h · alerts: browser
- @Sofia : made aware · area: tax filings · alerts: weekly email

## Waiting on

- [ask E91-A2: decide @Leo approve by @Marta aware @Jordi, @Sofia since 2026-11-09 row E91-S4] Is the car lease a business cost? — options: A) yes | B) no — recommend: A — unblocks: E91-S4
- [answered E91-A3 2026-11-10 @Leo · awaits @Marta · aware @Jordi] Two receipts under office costs? — answer: yes
- [answered E91-A4 2026-11-10 @Leo · approved @Marta 2026-11-11 · aware @Jordi] The VAT period? — answer: Q3 · done 2026-11-12 abc1234
- [ask E91-A5: decide @Marta aware @Jordi escalated by @Leo since 2026-11-10] The lease share? — escalated: @Leo: depends on the days
- [ask E91-A6: decide @Leo approve by @Marta since 2026-11-11] Book it? — sent back: @Marta: one is a meal (was: yes)
"""


def asks(text: str) -> tuple[list[dict], list[str]]:
    problems: list[str] = []
    return ask_refs.asks(text, Path("-"), Path("-"), problems), problems


class PeopleTests(unittest.TestCase):
    def test_four_roles_area_escalation_alerts(self) -> None:
        found, problems = people.parse(ROOT)
        self.assertEqual([], problems)
        self.assertEqual([("Jordi", "owner"), ("Marta", "expert"), ("Leo", "analyst"), ("Sofia", "aware")], [(p["handle"], p["role"]) for p in found])
        leo = found[2]
        self.assertEqual((["books"], "Marta", 24.0, "browser"), (leo["area"], leo["escalates_to"], leo["escalate_after_hours"], leo["alerts"]))
        self.assertEqual(["all"], found[0]["area"])

    def test_problems_name_the_form(self) -> None:
        _, problems = people.parse("## People\n\n- Leo is the analyst\n- @Leo : boss\n- @Ana : analyst · escalates to: @Ghost after 2 d\n")
        text = "\n".join(problems)
        for want in ("not a form the tools read", "role 'boss'", "@Ghost, who is not on the People list", "names no owner"):
            self.assertIn(want, text)
        self.assertEqual(([], []), people.parse("# x\n\n## Current State\n\nStatus: active\n"))

    def test_asks_name_who_approves_who_is_aware_who_escalated(self) -> None:
        got, problems = asks(ROOT)
        self.assertEqual([], problems)
        by = {a["code"]: a for a in got}
        self.assertEqual(("Leo", "Marta", ["Jordi", "Sofia"], "open"), (by["E91-A2"]["who"], by["E91-A2"]["approve_by"], by["E91-A2"]["aware"], by["E91-A2"]["state"]))
        self.assertEqual(("answered", "Marta", ["Jordi"]), (by["E91-A3"]["state"], by["E91-A3"]["awaits"], by["E91-A3"]["aware"]))
        self.assertEqual(("done", "Marta", "2026-11-11", "Q3"), (by["E91-A4"]["state"], by["E91-A4"]["approved_by"], by["E91-A4"]["approved_at"], by["E91-A4"]["answer"]))
        self.assertEqual(("Marta", "Leo", "@Leo: depends on the days", "The lease share?"), (by["E91-A5"]["who"], by["E91-A5"]["escalated_by"], by["E91-A5"]["escalated"], by["E91-A5"]["question"]))
        self.assertEqual("@Marta: one is a meal (was: yes)", by["E91-A6"]["sent_back"])

    def test_a_one_human_ask_carries_none_of_it(self) -> None:
        got, _ = asks("## Waiting on\n\n- [ask E4-A1: do @Jordi since 2026-10-01] Patch it — unblocks: S2\n")
        self.assertFalse({"approve_by", "aware", "escalated_by", "awaits", "approved_by"} & set(got[0]))

    def test_unknown_names(self) -> None:
        found, _ = people.parse(ROOT)
        nodes = [{"path": "docs/spines/x.md", "waiting_on": [{"code": "E1-A1", "who": "Ghost", "state": "open", "aware": ["Jordi"]}, {"code": "E1-A2", "who": "Leo", "approve_by": "Nobody", "state": "open"}]}]
        self.assertEqual(["docs/spines/x.md: ask E1-A1 names @Ghost, who is not on the People list", "docs/spines/x.md: ask E1-A2 names @Nobody, who is not on the People list"], people.unknown(found, nodes))
        self.assertEqual([], people.unknown([], nodes))


if __name__ == "__main__":
    unittest.main()
