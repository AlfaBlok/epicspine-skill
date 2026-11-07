"""tools/goal_tree.py (agent_team E43-S8, E43-S9): the public pages draw real goal trees and the voice-note fan-out.

Runs on this repo's own tree (the epicspine.dev crop), so it needs no other checkout.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("goal_tree", ROOT / "tools" / "goal_tree.py")
gt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gt)
CFG = json.loads((ROOT / "tools" / "goal-trees.json").read_text(encoding="utf-8"))


class GoalTreeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = CFG["trees"]["spine"]
        cls.tree = gt.build(cls.spec, gt.Repo(ROOT))

    def test_bigger_goals_above_smaller(self):
        levels = [n["level"] for n in gt.walk(self.tree)]
        self.assertEqual(levels[0], 0)
        for n in gt.walk(self.tree):
            for k in n["kids"]:
                self.assertEqual(k["level"], n["level"] + 1)

    def test_counts_and_more_come_from_the_repo(self):
        repo = gt.Repo(ROOT)
        goals, steps = repo.below(self.spec["root"]["path"])
        self.assertIn(f"{goals} goals and {steps} steps", self.tree["sub"])
        shown = len(self.spec["children"])
        more = [k for k in self.tree["kids"] if k["more"]]
        rest = len(repo.kids(self.spec["root"]["path"])) - shown
        self.assertEqual(bool(more), rest > 0)
        if more:
            self.assertIn(f"+{rest} more", more[0]["label"])

    def test_both_drawings_are_accessible_and_public(self):
        desc = gt.describe(self.tree)
        for svg in (gt.wide(gt.build(self.spec, gt.Repo(ROOT)), "gt-t", "t", desc), gt.narrow(gt.build(self.spec, gt.Repo(ROOT)), "gt-t", "t", desc)):
            self.assertRegex(svg, r'^<svg [^>]*role="img" aria-labelledby="gt-t-(wide|phone)-title gt-t-\1-desc"><title id=')
            text = re.sub(r"<[^>]+>", " ", svg).lower()
            for word in CFG["private"]:
                self.assertNotIn(word, text)
            self.assertNotIn("<line", svg)  # connectors are orthogonal paths

    def test_fan_counts_are_checked(self):
        text = "**Counts: 2 ready, 1 draft, 1 asks, 0 already covered, 1 for other teams.**\n| 1 | a |\n| 2 | b |\n| 3 | c |\n| 4 | d |\n"
        c = gt.counts(text)
        self.assertEqual((c["total"], c["placed"]), (4, 5))
        with self.assertRaises(SystemExit):
            gt.counts(text + "| 5 | e |\n| 6 | f |\n")

    def test_pages_carry_the_markers(self):
        for name, s in CFG["trees"].items():
            self.assertIn(f"<!-- goal-tree:{name} begin", (ROOT / s["page"]).read_text(encoding="utf-8"))
        self.assertIn("<!-- goal-tree:fan begin", (ROOT / CFG["fan"]["page"]).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
