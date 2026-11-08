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

    def test_glance_hides_extras_and_counts_them_in_more(self):
        """E43-S8 round 2: the at-a-glance tree leaves out "extra" items; its "+N more" counts them with the rest."""
        repo = gt.Repo(ROOT)
        full, glance = gt.build(self.spec, repo), gt.build(self.spec, repo, full=False)
        names = lambda t: {n["label"] for n in gt.walk(t) if not n["more"]}  # noqa: E731
        extras = {i["label"] for i in gt.walk_spec(self.spec) if i.get("extra")}
        self.assertTrue(extras)
        self.assertFalse(extras & names(glance))
        self.assertTrue(extras <= names(full))
        more = lambda t: next(k for k in t["kids"] if k["more"])["label"]  # noqa: E731
        n_full, n_glance = (int(re.search(r"\+(\d+)", more(t)).group(1)) for t in (full, glance))
        shown_extra = sum(1 for c in self.spec["children"] if c.get("extra"))
        self.assertEqual(n_glance, n_full + shown_extra)

    def test_fan_is_one_slide_with_two_real_cards(self):
        """E43-S9 round 2: the wide drawing is one 1200x520 slide, the phone one fits a 390x844 screen, both carry the
        two real cards as links and every part has its step of the animation."""
        c = {"ready": 10, "asks": 3, "draft": 7, "covered": 6, "other": 12, "total": 35, "placed": 38}
        wide = gt.fan_wide(c, 30, "7 November 2026", "f", "t", "d")
        phone = gt.fan_phone(c, 30, "7 November 2026", "f", "t", "d")
        self.assertIn('viewBox="0 0 1200 520"', wide)
        h = int(re.search(r'viewBox="0 0 360 (\d+)"', phone).group(1))
        self.assertLessEqual(h, 640)
        for svg in (wide, phone):
            self.assertEqual(svg.count("<image "), 2)
            self.assertEqual(svg.count('class="fan-card-link"'), 2)
            self.assertIn('data-s="5"', svg)
            self.assertIn('style="--ar:', svg)


if __name__ == "__main__":
    unittest.main()
