"""Shared tree library (scripts/spine_tree.py, references/tree-library.md): heat, stable ids, Recent changes, spine heat and ranking (Zenod EPIC-9 E9-5f)."""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import test_epic_log as E

import sys
sys.path.insert(0, str(E.SCRIPTS))
import spine_tree as T  # noqa: E402

PARITY = E.SCRIPTS.parent / "assets" / "tree-library-parity.json"


class HeatTests(unittest.TestCase):
    def test_half_life(self) -> None:
        self.assertEqual(1.0, T.heat(["2026-11-02"], "2026-11-02"))
        self.assertEqual(0.5, T.heat(["2026-10-19"], "2026-11-02"))
        self.assertEqual(0.25, T.heat(["2026-10-05"], "2026-11-02"))
        self.assertEqual(1.5, T.heat(["2026-11-02", "2026-10-19"], "2026-11-02"))

    def test_future_and_too_old_add_nothing(self) -> None:
        self.assertEqual(0.0, T.heat(["2026-11-03", "2026-07-04"], "2026-11-02"))
        self.assertGreater(T.heat(["2026-07-05"], "2026-11-02"), 0)

    def test_weight_is_the_share(self) -> None:
        self.assertEqual(0.5, T.heat([("2026-11-02", 0.5)], "2026-11-02"))

    def test_rounds_half_up_like_javascript(self) -> None:
        self.assertEqual(0.063, T.round3(0.0625))  # Python's round() gives 0.062


class IdTests(unittest.TestCase):
    def test_jaccard(self) -> None:
        self.assertEqual(0.5, T.jaccard("abc", "abd"))
        self.assertEqual(0.0, T.jaccard([], []))

    def test_overlap_keeps_the_id_below_the_threshold_a_new_one(self) -> None:
        self.assertEqual(["r-house"], T.match_ids({"r-house": "abc"}, ["abd"]))
        new = T.match_ids({"r-house": "abc"}, ["axy"])
        self.assertNotEqual(["r-house"], new)
        self.assertEqual(new, T.match_ids({"r-house": "abc"}, ["axy"]))  # deterministic
        self.assertEqual([T.new_id("axy")], new)

    def test_one_to_one_on_a_split_and_a_merge(self) -> None:
        split = T.match_ids({"r-house": "abcd"}, ["d", "abc"])
        self.assertEqual("r-house", split[1])
        self.assertNotEqual("r-house", split[0])
        self.assertEqual(["r-a"], T.match_ids({"r-a": "abc", "r-b": "d"}, ["abcd"]))

    def test_order_does_not_matter_and_new_ids_never_collide(self) -> None:
        self.assertEqual(["r-2", "r-1"], T.match_ids({"r-1": "ab", "r-2": "cd"}, ["cd", "ab"]))
        taken = T.new_id("xy")
        self.assertEqual([taken + "-2"], T.match_ids({taken: "pq"}, ["xy"]))


class RecentChangesTests(unittest.TestCase):
    PREV = {"h": {"name": "House", "kind": "working", "members": ["a", "b"]}, "t": {"name": "Trip", "kind": "working", "members": ["t"]}}

    def test_ops(self) -> None:
        cur = {"h": {"name": "Housing", "kind": "long-term", "members": ["a", "b", "c"]}, "g": {"name": "Agentine", "kind": "working", "members": ["g"]}}
        ops = [(c["op"], c["id"]) for c in T.recent_changes(self.PREV, cur)]
        self.assertEqual([("added", "g"), ("retired", "t"), ("renamed", "h"), ("moved", "h"), ("regrouped", "h")], ops)
        lines = T.rollup_recent(["- 2026-10-26 · new House"], T.recent_changes(self.PREV, cur), "2026-11-02", keep=3)
        self.assertEqual(["- 2026-11-02 · new Agentine", "- 2026-11-02 · retired Trip", "- 2026-11-02 · renamed House → Housing"], lines)

    def test_noop_keeps_the_section(self) -> None:
        self.assertEqual([], T.recent_changes(self.PREV, self.PREV))
        self.assertEqual(["- old"], T.rollup_recent(["- old", ""], [], "2026-11-02"))


class ParityFixtureTests(unittest.TestCase):
    """The shipped fixture is what Zenod's TypeScript port tests against: it must match this library."""

    def test_fixture_matches_the_library(self) -> None:
        doc = json.loads(PARITY.read_text(encoding="utf-8"))
        self.assertEqual({"HALF_LIFE_DAYS": T.HALF_LIFE_DAYS, "HORIZON_DAYS": T.HORIZON_DAYS, "MATCH_THRESHOLD": T.MATCH_THRESHOLD, "RECENT_CHANGES_KEEP": T.RECENT_CHANGES_KEEP}, doc["constants"])
        for c in doc["heat"]:
            events = [e if isinstance(e, str) else tuple(e) for e in c["events"]]
            self.assertEqual(c["expected"], T.heat(events, c["today"], c.get("half_life", T.HALF_LIFE_DAYS)), c["name"])
        for c in doc["match_ids"]:
            self.assertEqual(c["expected"], T.match_ids(c["previous"], c["current"]), c["name"])
        for c in doc["recent_changes"]:
            changes = T.recent_changes(c["previous"], c["current"])
            self.assertEqual(c["expected_changes"], changes, c["name"])
            self.assertEqual(c["expected_section"], T.rollup_recent(c["existing"], changes, c["day"]), c["name"])


class SpineHeatTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.today = datetime.date.today()
        self.git("init", "-q")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def git(self, *args: str, days_ago: int = 0) -> None:
        when = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%S")
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, env=env)

    def commit(self, path: str, text: str, days_ago: int = 0) -> None:
        (self.repo / path).parent.mkdir(parents=True, exist_ok=True)
        (self.repo / path).write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "x", days_ago=days_ago)

    def test_commit_days_count_once_and_text_dates_add(self) -> None:
        for n in range(3):
            self.commit("docs/a.md", f"a{n}")  # three commits today: one activity day
        self.commit("docs/b.md", "b", days_ago=28)
        day = lambda ago: (self.today - datetime.timedelta(days=ago)).isoformat()  # noqa: E731
        state = f"Last attempted: {day(0)} run x; before: {day(14)} run y"
        ledger = f"| Issue | Last Verified |\n|---|---|\n| E1-1 | {day(14)} |\n| E1-2 | {day(14)} |\n| E1-3 | 2099-01-01 |\n"
        got = T.spine_activity(self.repo, {"docs/a.md": {}, "docs/b.md": {"Current State": state, "Issue Ledger": ledger}}, self.today.isoformat())
        self.assertEqual({"heat": 1.0, "last_activity": day(0)}, got["docs/a.md"])
        self.assertEqual({"heat": 0.25 + 1.5 + 0.5, "last_activity": day(0)}, got["docs/b.md"])  # future row date ignored
        self.assertEqual(["docs/b.md", "docs/a.md"], T.rank(["docs/a.md", "docs/b.md"], {p: g["heat"] for p, g in got.items()}))

    def test_rank_ties_keep_tree_order_and_no_git_is_no_error(self) -> None:
        self.assertEqual(["x", "y", "z"], T.rank(["x", "y", "z"], {"x": 1, "y": 1}))
        with tempfile.TemporaryDirectory() as plain:
            self.assertEqual({"heat": 0.0, "last_activity": None}, T.spine_activity(Path(plain), {"a.md": {}}, "2026-11-02")["a.md"])


class SpinesJsonTests(E.EpicLogCase):
    def test_json_carries_heat_last_activity_and_ranked(self) -> None:
        self.new()
        log = self.log()
        for n in log["nodes"]:
            self.assertIn("heat", n)
            self.assertIn("last_activity", n)
        self.assertEqual(sorted(n["path"] for n in log["nodes"] if n["status"] in ("draft", "ready", "active", "blocked")), sorted(log["ranked"]))


if __name__ == "__main__":
    unittest.main()
