"""Desk intake (references/packs.md "Desk intake", scripts/pack_intake.py): the social pack's 6 kinds resolve, check() catches
broken targets and writers, and `pack.py social --wake-text` renders the rule a desk persona's prompt carries."""
from __future__ import annotations

import copy
import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"))
import pack  # noqa: E402
import pack_intake  # noqa: E402

SOCIAL = pack.load("social")


def broken(edit) -> list[str]:
    s = copy.deepcopy(SOCIAL)
    edit(s)
    return pack.check(s)


class SocialIntake(unittest.TestCase):
    def test_the_six_kinds_in_order(self) -> None:
        kinds = SOCIAL["intake"]["kinds"]
        self.assertEqual(["brief", "key_message", "priority", "idea", "big_idea", "feedback"], list(kinds))
        self.assertEqual([], pack_intake.check(SOCIAL))
        for k in kinds.values():
            self.assertIn("{link}", k["reply"])
            self.assertTrue(k["recognise"] and k["targets"] and k["writer"])

    def test_where_each_kind_lands(self) -> None:
        land = lambda key: [pack_intake.landing(SOCIAL, t)[1] for t in SOCIAL["intake"]["kinds"][key]["targets"]]  # noqa: E731
        self.assertIn("docs/spines/root.md#goal", land("brief"))
        self.assertIn("data/message-house.md#never-say", land("brief"))
        self.assertEqual(["data/message-house.md#points-to-emphasize"], land("key_message"))
        self.assertEqual(["data/directions.md#week", "data/directions.md#month", "data/directions.md#this-week-only"], land("priority"))
        self.assertEqual(["data/ideas.md", "data/assets.md"], land("idea"))
        self.assertEqual(["docs/spines/<slug>.md"], land("big_idea"))
        self.assertEqual(["data/posts-ledger.md", "data/message-house.md#feedback-log"], land("feedback"))
        self.assertEqual({"ideas.rows.from": "Jordi", "ideas.rows.state": "new"}, SOCIAL["intake"]["kinds"]["idea"]["set"])
        self.assertEqual("Delivery manager", SOCIAL["intake"]["kinds"]["big_idea"]["writer"])

    def test_anchor_is_githubs(self) -> None:
        self.assertEqual("#points-to-emphasize", pack_intake.anchor("Points to emphasize"))
        self.assertEqual("#weight-over--normal", pack_intake.anchor("Weight (over / normal)"))
        self.assertEqual("", pack_intake.anchor(None))


class IntakeCheck(unittest.TestCase):
    def test_unresolved_target(self) -> None:
        errs = broken(lambda s: s["intake"]["kinds"]["idea"]["targets"].append("ideas.nope"))
        self.assertIn("intake idea: target ideas.nope does not resolve (not a section, field or external)", errs)

    def test_writer_may_not_write_target(self) -> None:
        errs = broken(lambda s: s["intake"]["kinds"]["priority"].update(writer="Scout"))
        self.assertIn("intake priority: Scout may not write directions.week", errs)
        errs = broken(lambda s: s["intake"]["kinds"]["feedback"].update(writer="Writer"))
        self.assertIn("intake feedback: Writer may not write posts.rows.feedback", errs)
        errs = broken(lambda s: s["intake"]["kinds"]["big_idea"].update(writer="Jordi"))
        self.assertIn("intake big_idea: Jordi may not write spine", errs)

    def test_reply_must_name_where_it_landed(self) -> None:
        errs = broken(lambda s: s["intake"]["kinds"]["idea"].update(reply="Done."))
        self.assertIn("intake idea: reply does not name where it landed ({link})", errs)

    def test_set_values_and_fields(self) -> None:
        errs = broken(lambda s: s["intake"]["kinds"]["idea"]["set"].update({"ideas.rows.state": "posted?"}))
        self.assertTrue(any(e.startswith("intake idea: set ideas.rows.state = posted? not one of") for e in errs), errs)
        errs = broken(lambda s: s["intake"]["kinds"]["idea"]["set"].update({"posts.rows.status": "draft"}))
        self.assertIn("intake idea: set posts.rows.status is outside its targets", errs)
        errs = broken(lambda s: s["intake"]["kinds"]["idea"]["set"].update({"ideas.rows.nope": "x"}))
        self.assertIn("intake idea: set ideas.rows.nope is not a field", errs)

    def test_missing_parts_and_no_intake(self) -> None:
        errs = broken(lambda s: s["intake"]["kinds"]["brief"].pop("recognise"))
        self.assertIn("intake brief: no recognise", errs)
        self.assertEqual([], broken(lambda s: s.pop("intake")))


ROLE_TARGETS = {  # role -> (writable targets, status moves) the text must name
    "Scout": (["`data/topics.md`", "replace the table each run", "`data/ideas.md`", "every column but Why"], []),
    "Writer": (["`data/message-house.md` › Style rules", "`data/message-house.md` › Feedback log", "`data/ideas.md`: edit only Why", "`data/posts-ledger.md`", "every column but Link, Replies, Metrics, Result, Feedback"],
               ["`idea → draft`", "`draft → scheduled`", "`draft → held`", "`new → picked up`", "`parked → picked up`", "hold_rules", "`held → scheduled` is Jordi's alone"]),
    "Publisher": (["`data/posts-ledger.md`: edit only Link, Result"], ["`scheduled → posted`", "`scheduled → expired`", "link_present", "delete_live"]),
    "Responder": (["`data/posts-ledger.md`", "add rows", "every column but Feedback"], ["`draft → posted`", "`posted → measured`", "reply, outreach rows"]),
    "Engager": (["`data/posts-ledger.md`", "add rows", "every column but Replies, Feedback"], ["`draft → posted`", "`posted → measured`", "disclosure (Reddit)"]),
    "Reporter": (["edit only Replies, Metrics, Result", "`data/reports/<date>.md` › Numbers", "Cost"], ["`posted → measured`"]),
}


class RoleText(unittest.TestCase):
    def test_every_role_but_the_owner_has_a_text_naming_its_targets_and_moves(self) -> None:
        self.assertEqual(set(SOCIAL["roles"]) - {"Jordi"}, set(ROLE_TARGETS))
        for role, (targets, moves) in ROLE_TARGETS.items():
            text = pack_intake.role_text(SOCIAL, role)
            self.assertTrue(text.startswith(f"## Pack social: you are the {role}\n{SOCIAL['roles'][role].rstrip('.')}.\n"), role)
            for needle in targets + moves:
                self.assertIn(needle, text, f"{role}: {needle}")
            self.assertTrue(text.rstrip().endswith(f"Every step is a commit signed `Persona: {role}` (`EPICSPINE_PERSONA={role}`); the hook rejects an illegal transition."))
            if not moves:
                self.assertIn("- none", text)

    def test_a_role_is_told_only_its_own_moves(self) -> None:
        self.assertNotIn("`scheduled → posted`", pack_intake.role_text(SOCIAL, "Writer"))
        self.assertNotIn("`draft → scheduled`", pack_intake.role_text(SOCIAL, "Publisher"))
        self.assertNotIn("data/posts-ledger.md", pack_intake.role_text(SOCIAL, "Scout"))
        self.assertNotIn("`pulled`", pack_intake.role_text(SOCIAL, "Scout"))  # the Scout makes no post move

    def test_generated_from_the_schema_alone(self) -> None:
        s = copy.deepcopy(SOCIAL)
        s["lifecycles"]["post"]["transitions"].append({"from": "posted", "to": "expired", "by": ["Scout"], "when": "x"})
        self.assertIn("`posted → expired`: x", pack_intake.role_text(s, "Scout"))
        s["approval_gate"] = True
        self.assertIn("Nothing goes out without Jordi's approval.", pack_intake.role_text(s, "Writer"))

    def test_cli_role(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(0, pack.main(["social", "--wake-text", "--role", "writer"]))
        self.assertEqual(pack_intake.role_text(SOCIAL, "Writer"), out.getvalue())

    def test_the_owner_gets_the_desk_text(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(0, pack.main(["social", "--wake-text", "--role", "Jordi"]))
        self.assertEqual(pack_intake.wake_text(SOCIAL), out.getvalue())

    def test_unknown_role_exits_2_with_the_role_list(self) -> None:
        r = subprocess.run([sys.executable, "-B", str(Path(pack.__file__)), "social", "--wake-text", "--role", "Bob"], capture_output=True, text=True)
        self.assertEqual(2, r.returncode)
        self.assertEqual("", r.stdout)
        self.assertIn("no role Bob; roles: Jordi, Scout, Writer, Publisher, Responder, Engager, Reporter", r.stderr)


class WakeText(unittest.TestCase):
    def test_wake_text_names_every_kind_target_and_reply(self) -> None:
        text = pack_intake.wake_text(SOCIAL)
        self.assertTrue(text.startswith("## Desk intake (pack social): 6 kinds\n"))
        for label in ("Brief change", "Key message", "Priority", "Idea", "Big idea → epic", "Feedback on a post"):
            self.assertIn(f"**{label}**", text)
        for link in ("`data/directions.md#month`", "`data/ideas.md`", "`data/message-house.md#feedback-log`", "`docs/spines/<slug>.md`"):
            self.assertIn(link, text)
        self.assertIn("ask Jordi one line back", text)
        self.assertIn("Undo: revert {commit}", text)

    def test_cli(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(0, pack.main(["social", "--wake-text"]))
        self.assertEqual(pack_intake.wake_text(SOCIAL), out.getvalue())
        with redirect_stdout(io.StringIO()):
            self.assertEqual(0, pack.main(["check", "social"]))


if __name__ == "__main__":
    unittest.main()
