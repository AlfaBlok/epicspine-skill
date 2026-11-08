"""tools/feature_list.py (agent_team E43-S7 round 2): epicspine.dev/team/ draws EpicTeam's one feature list.

Uses a small list of its own, so it needs no agent_team checkout.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("feature_list", ROOT / "tools" / "feature_list.py")
fl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fl)

LIST = {"groups": [
    {"id": "main", "title": "What it does", "features": [
        {"id": "seats", "title": "One usage limit never stops the work.", "text": "One pool.", "rows": ["EPIC-50"], "section": "seats"}]},
    {"id": "inbox-focus", "title": "Keeps your inbox focused, no context overload", "intro": "Only what needs you.", "features": [
        {"id": "one", "title": "One page, one card", "text": "One card per page, never one per task.", "rows": ["E43-S7"]},
        {"id": "two", "title": "Snooze what can wait", "text": "It comes back by itself.", "rows": ["E48-S3"]}]},
]}


class FeatureListTest(unittest.TestCase):
    def test_lists_a_group_and_leaves_features_with_their_own_section_to_it(self):
        out = fl.render(LIST)
        self.assertIn('id="inbox-focus"', out)
        self.assertIn("Keeps your inbox focused, no context overload.</h2>", out)
        self.assertEqual(out.count("<li>"), 2)
        self.assertNotIn("One usage limit", out)
        self.assertNotIn("E43-S7", out)

    def test_refuses_row_codes_and_paths_in_public_words(self):
        bad = json.loads(json.dumps(LIST))
        bad["groups"][1]["features"][0]["text"] = "Built by E43-S7."
        with self.assertRaises(SystemExit):
            fl.render(bad)

    def test_writes_between_the_markers_and_check_sees_drift(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "agent_team"
            (repo / "docs" / "features").mkdir(parents=True)
            (repo / "docs" / "features" / "epicteam.json").write_text(json.dumps(LIST), encoding="utf-8")
            page = Path(d) / "index.html"
            page.write_text("<main>\n<!-- features:team begin (tools/feature_list.py writes this) -->\n<!-- features:team end -->\n</main>\n", encoding="utf-8")
            old_site, old_lists = fl.SITE, fl.LISTS
            fl.SITE, fl.LISTS = Path(d), {"team": {"page": "index.html", "repo": "agent_team", "file": "docs/features/epicteam.json"}}
            try:
                self.assertEqual(fl.main(["--check", "--repo", f"agent_team={repo}"]), 1)
                self.assertEqual(fl.main(["--repo", f"agent_team={repo}"]), 0)
                self.assertEqual(fl.main(["--check", "--repo", f"agent_team={repo}"]), 0)
                self.assertIn("One page, one card", page.read_text(encoding="utf-8"))
            finally:
                fl.SITE, fl.LISTS = old_site, old_lists

    def test_the_team_page_carries_the_markers(self):
        text = (ROOT / "team" / "index.html").read_text(encoding="utf-8")
        self.assertIn("<!-- features:team begin (tools/feature_list.py writes this) -->", text)
        self.assertIn('id="inbox-focus"', text)


if __name__ == "__main__":
    unittest.main()
