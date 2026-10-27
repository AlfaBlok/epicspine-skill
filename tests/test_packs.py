"""Packs (references/packs.md, scripts/pack.py): the social schema loads and is self-consistent; check() catches broken schemas."""
from __future__ import annotations

import copy
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"))
import pack  # noqa: E402

SOCIAL = pack.load("social")


class SocialPack(unittest.TestCase):
    def test_social_ships_and_is_sound(self) -> None:
        self.assertIn("social", pack.available())
        self.assertEqual("social", SOCIAL["pack"])
        self.assertEqual([], pack.check(SOCIAL))

    def test_the_seven_files_and_their_paths(self) -> None:
        paths = {k: f["path"] for k, f in SOCIAL["files"].items()}
        self.assertEqual({
            "brief": "data/brief.md", "directions": "data/directions.md", "topics": "data/topics.md",
            "ideas": "data/ideas.md", "posts": "data/posts-ledger.md", "assets": "data/assets.md",
            "reports": "data/reports/{date}.md",
        }, paths)
        brief = SOCIAL["files"]["brief"]["sections"]
        for key in ("objective", "key_messages", "voice", "formats", "examples", "hold_rules"):
            self.assertIn(key, brief)
        self.assertIn("weight", brief["key_messages"]["fields"])
        self.assertLessEqual({"Week", "Month"}, {s["heading"] for s in SOCIAL["files"]["directions"]["sections"].values()})
        posts = SOCIAL["files"]["posts"]["sections"]["rows"]["fields"]
        for key in ("messages", "link", "feedback", "status"):
            self.assertIn(key, posts)

    def test_post_statuses_and_no_approval_gate(self) -> None:
        lc = SOCIAL["lifecycles"]["post"]
        self.assertEqual({"idea", "draft", "scheduled", "posted", "measured", "held", "pulled", "expired"}, set(lc["states"]))
        self.assertEqual(["idea", "draft", "scheduled", "posted", "measured"], lc["path"])
        self.assertIs(False, SOCIAL["approval_gate"])
        self.assertFalse({"approved", "approval", "review"} & set(lc["states"]))
        for a, b in zip(lc["path"], lc["path"][1:]):  # C1: nothing on the way out waits for Jordi
            by = {r for t in lc["transitions"] if (t["from"], t["to"]) == (a, b) for r in t["by"]}
            self.assertTrue(by - {"Jordi"}, f"{a} -> {b}")

    def test_every_status_reachable_and_dead_ends_are_terminal(self) -> None:
        for name, lc in SOCIAL["lifecycles"].items():
            with self.subTest(lifecycle=name):
                self.assertEqual(set(lc["states"]), pack.reachable(lc))
                ends = set(lc["states"]) - {t["from"] for t in lc["transitions"]}
                self.assertEqual({"post": {"pulled", "expired"}, "idea": {"posted", "epic"}}[name], ends)

    def test_pull_deletes_a_live_post_and_only_jordi_pulls_or_releases(self) -> None:
        lc = SOCIAL["lifecycles"]["post"]
        pulls = {t["from"]: t for t in lc["transitions"] if t["to"] == "pulled"}
        self.assertEqual({"draft", "held", "scheduled", "posted", "measured"}, set(pulls))
        self.assertEqual("delete_live", pulls["posted"]["effect"])  # C5
        mine = [t for t in lc["transitions"] if t["to"] == "pulled" or t["from"] == "held" and t["to"] == "scheduled"]
        self.assertTrue(all(t["by"] == ["Jordi"] for t in mine))

    def test_every_file_and_field_has_a_writer_from_the_role_list(self) -> None:
        roles = {"Jordi", "Scout", "Writer", "Publisher", "Responder", "Engager", "Reporter"}
        self.assertEqual(roles, set(SOCIAL["roles"]))
        for fkey, who in pack.writers(SOCIAL).items():
            with self.subTest(file=fkey):
                self.assertTrue(who)
                self.assertLessEqual(who, roles)
        for addr, fld in pack.fields(SOCIAL).items():
            if "computed" not in fld:
                self.assertTrue(pack.field_writers(SOCIAL, addr), addr)
        self.assertEqual({"Jordi"}, pack.field_writers(SOCIAL, "posts.rows.feedback"))
        self.assertEqual({"Publisher", "Responder", "Engager"}, pack.field_writers(SOCIAL, "posts.rows.link"))
        self.assertEqual({"Writer"}, pack.field_writers(SOCIAL, "ideas.rows.state"))

    def test_repeat_feedback_becomes_a_style_rule_with_undo(self) -> None:
        rule = SOCIAL["rules"]["style_rule_from_feedback"]  # C6
        self.assertEqual((2, "brief.style_rules"), (rule["repeats"], rule["to"]))
        self.assertTrue(rule["undo"])


class Check(unittest.TestCase):
    def broken(self, edit) -> list[str]:
        s = copy.deepcopy(SOCIAL)
        edit(s)
        return pack.check(s)

    def test_unreachable_status(self) -> None:
        errs = self.broken(lambda s: s["lifecycles"]["post"]["states"].update(limbo="x"))
        self.assertIn("lifecycle post: limbo unreachable from idea", errs)

    def test_file_without_writer(self) -> None:
        def strip(s):
            s["files"]["reports"]["sections"] = {"numbers": {"heading": "Numbers", "shape": "text", "writers": []}}
        errs = self.broken(strip)
        self.assertIn("file reports: no writer", errs)
        self.assertIn("reports.numbers: no writer", errs)

    def test_unknown_role_state_and_ref(self) -> None:
        def edit(s):
            s["lifecycles"]["post"]["transitions"].append({"from": "posted", "to": "gone", "by": ["Intern"]})
            s["files"]["posts"]["sections"]["rows"]["fields"]["topic"]["ref"] = ["topics.nope"]
        errs = self.broken(edit)
        self.assertIn("lifecycle post: posted -> gone: unknown state gone", errs)
        self.assertIn("lifecycle post: posted -> gone: unknown role Intern", errs)
        self.assertIn("posts.rows.topic: ref to unknown section topics.nope", errs)

    def test_a_gate_on_the_path_is_caught(self) -> None:
        def gate(s):
            for t in s["lifecycles"]["post"]["transitions"]:
                if (t["from"], t["to"]) == ("draft", "scheduled"):
                    t["by"] = ["Jordi"]
        errs = self.broken(gate)
        self.assertIn("lifecycle post: path step draft -> scheduled waits on Jordi (approval_gate is false)", errs)

    def test_cli_check_exit_code(self) -> None:
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(0, pack.main(["check", "social"]))
        self.assertIn("social: ok", out.getvalue())


class OptIn(unittest.TestCase):
    def test_agents_line_turns_packs_on(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self.assertEqual([], pack.enabled(repo))
            (repo / "AGENTS.md").write_text("# AGENTS\n\nIntegration policy: main-direct\n")
            self.assertEqual([], pack.enabled(repo))
            (repo / "AGENTS.md").write_text("# AGENTS\n\nPack: social\nEpicSpine packs: Social, sales\n")
            self.assertEqual(["social", "sales"], pack.enabled(repo))


if __name__ == "__main__":
    unittest.main()
