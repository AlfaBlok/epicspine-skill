"""Pack export (scripts/pack_export.py, `pack.py social --json`): fixture repo -> golden JSON, missing files, computed back-links, zenod-social's real data."""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"))
import pack  # noqa: E402
import pack_export  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "pack_social"
GOLDEN = Path(__file__).parent / "fixtures" / "pack_social.golden.json"
ZENOD = Path("/home/t3agent/github/zenod-social")
NOW = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
TOP = ["schemaVersion", "pack", "packVersion", "repo", "generatedAt", "warnings",
       "brief", "directions", "topics", "ideas", "posts", "assets", "reports", "sources"]


def fixture() -> dict:
    return {**pack_export.export("social", FIXTURE, NOW), "repo": "<repo>"}


class Golden(unittest.TestCase):
    def test_fixture_repo_matches_the_golden_json(self) -> None:
        # regenerate after a deliberate contract change, then review the diff: see references/packs.md
        self.assertEqual(json.loads(GOLDEN.read_text(encoding="utf-8")), fixture())

    def test_top_level_shape(self) -> None:
        d = fixture()
        self.assertEqual(TOP, list(d))
        self.assertEqual((1, "social", "2026-10-27T12:00:00Z"), (d["schemaVersion"], d["pack"], d["generatedAt"]))
        self.assertEqual(set(pack.load("social")["files"]["brief"]["sections"]), set(d["brief"]))
        self.assertEqual({"week", "do_dont", "voice_note", "month"}, set(d["directions"]))

    def test_sections_living_in_other_files(self) -> None:
        d = fixture()
        self.assertTrue(d["brief"]["objective"].startswith("Acme becomes"))
        self.assertEqual("docs/spines/root.md", d["sources"]["brief.objective"]["path"])
        self.assertEqual("data/message-house.md", d["sources"]["brief.voice"]["path"])
        self.assertEqual(["First person singular on Reddit.", "Plain words, no jargon."], d["brief"]["voice"])
        self.assertEqual("Developers who keep notes in plain files.", d["brief"]["audience"])

    def test_typed_cells(self) -> None:
        p1 = fixture()["posts"][0]
        self.assertEqual(["A-1"], p1["assets"])
        self.assertEqual(["1", "2"], p1["messages"])
        self.assertEqual(("T-1026-1", "H1", "I-1"), (p1["topic"], p1["highlight"], p1["idea"]))
        self.assertEqual("https://x.com/acme/status/10", p1["link"])  # markdown link -> the URL
        self.assertEqual((3, "measured", "more like this"), (p1["replies"], p1["status"], p1["feedback"]))
        self.assertEqual("Every change is a commit | see the diagram", p1["text"])  # \| is a literal pipe
        self.assertIsNone(p1["community"])
        self.assertEqual([60, 40], [f["share"] for f in fixture()["brief"]["formats"]])

    def test_computed_back_links(self) -> None:
        d = fixture()
        self.assertEqual({"A-1": ["P-0001", "P-0003"], "A-2": []}, {a["id"]: a["used_by"] for a in d["assets"]})
        self.assertEqual({"1": ["P-0001", "P-0002"], "2": ["P-0001"]}, {m["id"]: m["carried_by"] for m in d["brief"]["key_messages"]})
        self.assertEqual(["P-0001", "P-0003"], d["directions"]["week"][0]["served_by"])
        self.assertEqual([], d["directions"]["month"][0]["served_by"])
        self.assertEqual({"I-1": ["P-0001"], "I-2": []}, {i["id"]: i["became"] for i in d["ideas"]})
        self.assertEqual(["P-0001"], d["topics"][0]["used_by"])

    def test_bad_rows_warn_and_never_crash(self) -> None:
        d = fixture()
        msgs = {(w["file"], w["line"], w["message"]) for w in d["warnings"]}
        self.assertIn(("data/posts-ledger.md", 8, "row skipped: 24 cells under 22 columns (unescaped |?)"), msgs)
        self.assertIn(("data/topics.md", 6, "heat: not a number: 'high'"), msgs)
        self.assertIn(("data/posts-ledger.md", 7, "assets: A-9 not found in assets.rows"), msgs)
        self.assertNotIn("T-0999-9", json.dumps(d["warnings"]))  # topics are replaced daily: old ids are not dangling
        self.assertEqual(["P-0001", "P-0002", "P-0003"], [p["id"] for p in d["posts"]])
        self.assertEqual("approved", d["posts"][2]["status"])  # kept as written, and warned
        self.assertTrue(any("'approved' not one of" in w["message"] for w in d["warnings"]))


class Missing(unittest.TestCase):
    def test_an_empty_repo_gives_empty_values_and_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = pack_export.export("social", Path(tmp), NOW)
        for key in ("topics", "ideas", "posts", "assets", "reports"):
            self.assertEqual([], d[key], key)
        self.assertIsNone(d["brief"]["objective"])
        self.assertEqual([], d["brief"]["key_messages"])
        self.assertEqual([], d["directions"]["week"])
        self.assertFalse(any(s["exists"] for s in d["sources"].values()))
        missing = {w["file"] for w in d["warnings"] if w["message"] == "file missing"}
        self.assertEqual({"docs/spines/root.md", "data/brief.md", "data/message-house.md", "data/directions.md",
                          "data/topics.md", "data/ideas.md", "data/posts-ledger.md", "data/assets.md"}, missing)
        self.assertIn({"file": "data/reports/{date}.md", "line": None, "message": "no files"}, d["warnings"])
        self.assertIn("no 'Pack: social' line", d["warnings"][0]["message"])

    def test_a_missing_section_and_a_missing_column(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "data").mkdir()
            (Path(tmp) / "data" / "directions.md").write_text("# D\n\n## Week\n\n| Id | Highlight |\n|---|---|\n| H1 | x |\n")
            d = pack_export.export("social", Path(tmp), NOW)
        self.assertEqual([{"id": "H1", "highlight": "x", "why": None, "until": None, "served_by": [], "_line": 7}], d["directions"]["week"])
        msgs = [w["message"] for w in d["warnings"] if w["file"] == "data/directions.md"]
        self.assertIn("missing column(s): Why, Until", msgs)
        self.assertIn("no 'Month' section (directions.month)", msgs)


class Cli(unittest.TestCase):
    def test_pack_py_social_json(self) -> None:
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(0, pack.main(["social", "--json", "--repo", str(FIXTURE)]))
        d = json.loads(out.getvalue())
        self.assertEqual(TOP, list(d))
        self.assertEqual(str(FIXTURE.resolve()), d["repo"])


@unittest.skipUnless((ZENOD / "data" / "posts-ledger.md").is_file(), "no zenod-social checkout")
class RealShape(unittest.TestCase):
    def test_zenod_social_current_data_exports(self) -> None:
        d = pack_export.export("social", ZENOD)  # read-only
        self.assertEqual(TOP, list(d))
        self.assertGreater(len(d["posts"]), 0)
        self.assertTrue(all(p["date"] and p["status"] for p in d["posts"]))
        self.assertTrue(d["brief"]["objective"])
        self.assertTrue(all(set(w) == {"file", "line", "message"} for w in d["warnings"]))


if __name__ == "__main__":
    unittest.main()
