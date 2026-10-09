from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
SKILL_DIR = REPO / "skill" / "epic-spine"
SCRIPT = SKILL_DIR / "scripts" / "build_shortlist.py"
TEMPLATE = SKILL_DIR / "assets" / "shortlist.template.html"
SAMPLE = SKILL_DIR / "assets" / "shortlist-sample.json"

SPEC = importlib.util.spec_from_file_location("build_shortlist", SCRIPT)
assert SPEC and SPEC.loader
build_shortlist = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = build_shortlist
SPEC.loader.exec_module(build_shortlist)


def load_sample() -> dict:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


class ShortlistBuilderTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-shortlist-")
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def build(self, data: dict) -> str:
        src = self.tmp / "shortlist.json"
        out = self.tmp / "shortlist.html"
        src.write_text(json.dumps(data), encoding="utf-8")
        build_shortlist.build(src, out)
        return out.read_text(encoding="utf-8")

    def test_sample_builds_with_every_item(self) -> None:
        data = load_sample()
        html = self.build(data)
        for item in data["items"]:
            self.assertIn(item["name"], html)
        self.assertIn("build_shortlist.py", html)

    def test_escapes_script_injected_in_name(self) -> None:
        data = load_sample()
        data["items"][0]["name"] = "<script>alert(1)</script>"
        html = self.build(data)
        self.assertNotIn("<script>alert", html)
        self.assertIn("\\u003cscript>alert(1)\\u003c/script>", html)
        self.assertEqual(1, html.count("</script>"), "only the page script may close")

    def test_escapes_injected_markup_in_title(self) -> None:
        data = load_sample()
        data["title"] = "<b>Title</b>"
        html = self.build(data)
        self.assertNotIn("<b>Title</b>", html)
        self.assertIn("&lt;b&gt;Title&lt;/b&gt;", html)

    def test_rejects_unknown_status(self) -> None:
        data = load_sample()
        data["items"][0]["status"] = "maybe"
        with self.assertRaises(build_shortlist.ShortlistError) as caught:
            self.build(data)
        self.assertIn("status", str(caught.exception))

    def test_rejects_rejected_without_reason(self) -> None:
        data = load_sample()
        item = data["items"][0]
        item["status"] = "rejected"
        item.pop("rejectedReason", None)
        with self.assertRaises(build_shortlist.ShortlistError) as caught:
            self.build(data)
        self.assertIn("rejectedReason", str(caught.exception))

    def test_rejects_duplicate_ids(self) -> None:
        data = load_sample()
        data["items"][1]["id"] = data["items"][0]["id"]
        with self.assertRaises(build_shortlist.ShortlistError) as caught:
            self.build(data)
        self.assertIn("duplicate id", str(caught.exception))

    def test_rejects_missing_required_fields(self) -> None:
        data = load_sample()
        del data["title"]
        with self.assertRaises(build_shortlist.ShortlistError):
            self.build(data)

    def test_table_precedes_criteria_section(self) -> None:
        # The page leads with the table; criteria must move below it.
        html = self.build(load_sample())
        self.assertLess(html.index('id="slbody"'), html.index('id="criteria"'))


class ShortlistTemplateTest(unittest.TestCase):
    def test_template_works_offline_no_network_references(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8").lower()
        for needle in ("http://", "https://", "//cdn", "cdn.", "unpkg", "leaflet", "integrity="):
            with self.subTest(needle=needle):
                self.assertNotIn(needle, text)

    def test_template_has_sort_and_filters(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        for token in ("starredOnly", 'id="status"', 'id="area"', 'id="tag"', "data-sort"):
            with self.subTest(token=token):
                self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
