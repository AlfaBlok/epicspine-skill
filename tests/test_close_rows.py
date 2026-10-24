"""Closed epics close their rows (agent_team EPIC-16 E16-S1): the `superseded` row status, the sweep on close
(`spine_fix.py --close`), the `closed-rows` advisory and `tree_audit.py`."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_epic_log import SCRIPTS, EpicLogCase
from test_status_true import BASE
from test_validate_spine import validate_spine as validator

sys.path.insert(0, str(SCRIPTS))
import close_rows  # noqa: E402
import epic_log  # noqa: E402
import personas  # noqa: E402
import spine_fix  # noqa: E402

HEAD = "| draft | Ticket worker | example-worker | Review CLI explanation | draft | none | codex/example | 6f63d378 | Synthetic draft only | 2026-09-06 | Read acceptance command |"
OUTCOME = "## Outcome\n\nVerdict: superseded\nOutcome: Replaced by the sprint.\nClosed: 2026-10-20 by DM\nRisk: none\n\n"


def row(status: str, action: str = "Read acceptance command") -> str:
    return HEAD.replace("| draft | none", f"| {status} | none").replace("| Read acceptance command |", f"| {action} |")


def spine(status: str = "done", rows: tuple[str, ...] = ("ready",), sup: str = "[Next](NEXT.md)", outcome: str = OUTCOME) -> str:
    text = BASE.replace("Status: ready", f"Status: {status}").replace("- [ ] DOD-1", "- [x] DOD-1")
    text = text.replace(HEAD, "\n".join(row(s) for s in rows))
    text = text.replace("Integration branch: codex/example\n", f"Integration branch: codex/example\nSuperseded by: {sup}\n" if sup else "Integration branch: codex/example\n")
    return text.replace("## Current State", outcome + "## Current State", 1)


class VocabularyTests(unittest.TestCase):
    def test_superseded_is_a_closed_row_status_not_done(self) -> None:
        for word in ("superseded", "dropped", "Obsolete", "wontfix", "cancelled", "abandoned"):
            self.assertEqual("superseded", spine_fix.row_word(word), word)
            self.assertFalse(spine_fix.row_open(word), word)
        self.assertEqual("superseded", spine_fix.row_word("superseded by fix-lap retest"))
        self.assertNotIn("superseded", personas.OPEN)
        self.assertIn("superseded", validator.TRACKABLE_STATUSES)

    def test_open_and_done_like_words(self) -> None:
        for word in ("draft", "ready", "active", "blocked", "review", "testing", "ready-for-test", "partial / open", "blocked / package merged", "queued", "in progress"):
            self.assertTrue(spine_fix.row_open(word), word)
        for word in ("done", "Done / integrated", "deferred", "on hold", "integrated PR1266", "live verified", "merged; CI pass", "", "<status>"):
            self.assertFalse(spine_fix.row_open(word), word)

    def test_fix_maps_ledger_synonyms_to_superseded(self) -> None:
        new, what = spine_fix.fix_text(BASE.replace("| draft | none", "| cancelled | none"))
        self.assertIn("| superseded | none", new)
        self.assertEqual(["ledger Status 'cancelled' -> superseded"], what)

    def test_a_superseded_child_rolls_up_as_done(self) -> None:
        self.assertEqual("done", epic_log.rollup("active", ["done", "superseded"], []))


class SweepTests(unittest.TestCase):
    def test_open_rows_become_superseded_with_a_note(self) -> None:
        text = spine(rows=("ready", "blocked / waits", "done", "deferred", "superseded", "ready-for-test"))
        new, what = close_rows.close_rows(text, "2026-10-24")
        note = "closed with epic 2026-10-20; successor: [Next](NEXT.md)"
        self.assertEqual([f"3 open rows -> superseded (ready 1, blocked / waits 1, ready-for-test 1); {note}"], what)
        self.assertEqual(3, new.count(f"| superseded | none | codex/example | 6f63d378 | Synthetic draft only | 2026-09-06 | Read acceptance command · {note} |"))
        for kept in ("| done | none", "| deferred | none", "| superseded | none | codex/example | 6f63d378 | Synthetic draft only | 2026-09-06 | Read acceptance command |"):
            self.assertIn(kept, new)
        self.assertEqual((new, []), close_rows.close_rows(new, "2026-10-25"))  # idempotent
        self.assertEqual(0, close_rows.open_rows(new))

    def test_status_done_without_superseded_by_and_without_outcome_date(self) -> None:
        new, what = close_rows.close_rows(spine(sup="", outcome="", rows=("draft",)), "2026-10-24")
        self.assertIn("closed with epic 2026-10-24; successor: none", what[0])
        self.assertIn("| superseded | none", new)

    def test_open_epics_are_never_swept(self) -> None:
        for status in ("active", "ready", "draft", "blocked", "deferred"):
            text = spine(status=status, sup="", rows=("ready",))
            self.assertEqual((text, []), close_rows.close_rows(text, "2026-10-24"), status)
            self.assertEqual(0, close_rows.open_rows(text))
        superseded = spine(status="active", rows=("ready",))  # a `Superseded by:` header closes it
        self.assertEqual(1, close_rows.open_rows(superseded))

    def test_no_next_action_column_or_short_row_notes_the_epic(self) -> None:
        text = spine(rows=("ready",)).replace("| Last Verified | Next Action |", "| Last Verified | Notes |")
        new, _ = close_rows.close_rows(text, "2026-10-24")
        self.assertIn("Next action: Run the validator against this file. · ledger: closed with epic 2026-10-20", new)
        short = spine(rows=("ready",)).replace(" Read acceptance command |", "")
        new, _ = close_rows.close_rows(short, "2026-10-24")
        self.assertIn("| superseded | none | codex/example | 6f63d378 | Synthetic draft only | 2026-09-06 |\n", new)
        self.assertIn("· ledger: closed with epic", new)

    def test_cli_dry_run_by_default_then_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "epic.md"
            path.write_text(text := spine(rows=("ready", "active")))
            run = lambda *a: subprocess.run([sys.executable, "-B", str(SCRIPTS / "spine_fix.py"), "--close", *a, str(path)], capture_output=True, text=True)  # noqa: E731
            dry = run()
            self.assertIn("would close: 2 open rows", dry.stdout)
            self.assertIn("dry run", dry.stdout)
            self.assertEqual(text, path.read_text())
            self.assertIn("closed: 2 open rows", run("--write").stdout)
            self.assertIn("nothing to close", run("--write").stdout)
            self.assertEqual([], validator.validate_local(path).errors)


class AdvisoryTests(unittest.TestCase):
    def check(self, text: str) -> tuple[list[str], bool]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "epic.md"
            path.write_text(text)
            doc = validator.validate_local(path)
        return [w for w in doc.warnings if w.startswith("closed-rows")], doc.fails(strict=True)

    def test_finished_epic_with_open_rows_is_advisory_never_a_block(self) -> None:
        found, fails = self.check(spine(rows=("ready", "blocked")))
        self.assertEqual(["closed-rows: finished epic with 2 open rows: run `spine_fix.py --close --write <this spine>` (they become superseded)"], found)
        self.assertFalse(fails)
        self.assertEqual([], self.check(spine(rows=("done", "superseded")))[0])
        self.assertEqual([], self.check(spine(status="active", sup="", rows=("ready",)))[0])


class TreeAuditTests(EpicLogCase):
    def audit(self, *args: str) -> subprocess.CompletedProcess:
        return self.run_script("tree_audit.py", *args)

    def test_groups_and_the_sweep_command(self) -> None:
        self.new("docs/a.md", title="alpha")
        self.write("docs/a.md", spine(rows=("ready", "ready-for-test")).replace("Spine ID: synthetic-compact-example", "Spine ID: a\nParent spine: [Root](root.md)"))
        self.new("docs/b.md", title="beta")
        b = self.repo / "docs/b.md"
        b.write_text(b.read_text().replace("Status: draft", "Status: SHIP candidate") + "\n" * 160)
        result = json.loads(self.audit("--json").stdout)
        self.assertEqual([{"path": "docs/a.md", "open_rows": 2}], result["finished_with_open_rows"])
        self.assertIn({"path": "docs/b.md", "status": "SHIP candidate"}, result["nonstandard_status"])
        self.assertEqual({"ready-for-test": 1}, result["nonstandard_row_words"])
        self.assertEqual(["docs/b.md"], [o["path"] for o in result["over_budget"]])
        self.assertEqual("docs/root.md", result["root"]["path"])
        self.assertTrue(result["sweep"].endswith("spine_fix.py --close --write docs/a.md"))
        text = self.audit().stdout
        self.assertIn("finished epics with open rows: 1 (2 rows)", text)
        self.assertIn("fix (preview without --write):", text)
        before = (self.repo / "docs/a.md").read_text()
        subprocess.run(result["sweep"], shell=True, capture_output=True, check=True)
        self.assertNotEqual(before, (self.repo / "docs/a.md").read_text())
        self.assertEqual([], json.loads(self.audit("--json").stdout)["finished_with_open_rows"])

    def test_routing_that_names_a_closed_epic(self) -> None:
        self.new("docs/a.md", title="alpha")
        self.write("docs/a.md", spine(rows=("done",)).replace("Spine ID: synthetic-compact-example", "Spine ID: a\nParent spine: [Root](root.md)"))
        self.new("docs/live.md", title="live")
        self.write("AGENTS.md", "# Start here\nActive surface: docs/a.md\nAlso docs/live.md\n<!-- epicspine:begin x -->\nsee docs/a.md\n<!-- epicspine:end -->\n")
        self.write("README.md", "Read [alpha](docs/a.md) first.\n")
        result = json.loads(self.audit("--json").stdout)
        self.assertEqual([{"file": "AGENTS.md", "line": 2, "epic": "docs/a.md"}, {"file": "README.md", "line": 1, "epic": "docs/a.md"}], result["routing"])
        self.assertIn("routing names closed epic: AGENTS.md:2 docs/a.md", self.audit().stdout)

    def test_undecided_and_root_age_read_git(self) -> None:
        self.new("docs/c.md", title="gamma")
        env = {**os.environ, "GIT_AUTHOR_DATE": "2026-01-01T00:00:00", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00"}
        git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=self.repo, env=env, capture_output=True, check=True)  # noqa: E731
        git("init", "-q")
        git("add", "-A")
        git("commit", "-qm", "old")
        result = json.loads(self.audit("--json").stdout)
        self.assertIn("docs/c.md", [u["path"] for u in result["undecided"]])
        self.assertGreaterEqual(result["root"]["days"], 14)


if __name__ == "__main__":
    unittest.main()
