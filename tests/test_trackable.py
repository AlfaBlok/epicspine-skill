from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_agents_block import agents_block
from test_validate_spine import validate_spine as v, VALIDATOR_PATH

SPINE = """# EPIC: T

Spine ID: t
{extra}
## Current State

Status: {status}
Waiting on: none

## Definition Of Done

{done}

## Issue Ledger

{ledger}
"""
LEDGER = "| Issue | Title | Owner | Status |\n|---|---|---|---|\n| draft | A | me | draft |"
TICKET = "# T\n\nTicket ID: R-1\nStatus: {status}\nOwner: me\n\n## {head}\n\n{body}\n"
GOOD = {"extra": "", "status": "active — building", "done": "- [ ] ship", "ledger": LEDGER}


class TrackableTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-trackable-")
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def check(self, text: str, name: str = "doc.md") -> dict:
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return v.trackable(path)

    def spine(self, **changes: str) -> dict:
        return self.check(SPINE.format(**{**GOOD, **changes}))

    def test_good_spine_and_vocabulary(self) -> None:
        self.assertEqual([], self.spine()["missing"])
        for status in ("draft", "READY", "Active.", "blocked: x", "done", "deferred"):
            self.assertTrue(self.spine(status=status)["trackable"], status)
        for status in ("review", "planning", "", "draft | ready | active", "closed"):
            self.assertFalse(self.spine(status=status)["trackable"], status)

    def test_checkbox_rules(self) -> None:
        self.assertTrue(self.spine(done="- [x] a\n- [X] b")["trackable"])
        result = self.spine(done="Prose only.")
        self.assertEqual(["checkbox under ## Definition Of Done"], result["missing"])
        self.assertFalse(self.spine(done="* [ ] bullet")["trackable"])

    def test_ledger_needs_status_column_but_may_be_absent(self) -> None:
        bad = "| Issue | Title | Owner |\n|---|---|---|\n| draft | A | me |"
        self.assertEqual(["Issue Ledger Status column"], self.spine(ledger=bad)["missing"])
        text = SPINE.format(**GOOD).split("## Issue Ledger")[0]
        self.assertTrue(self.check(text)["trackable"])

    def test_local_backend_checks_ticket_files(self) -> None:
        ledger = "| Ticket | Depends On |\n|---|---|\n| [R-1](tickets/R-1.md) | none |\n| [R-2](tickets/R-2.md) | none |"
        (self.dir / "tickets").mkdir()
        (self.dir / "tickets/R-1.md").write_text(TICKET.format(status="ready", head="Acceptance", body="- [ ] x"))
        (self.dir / "tickets/R-2.md").write_text(TICKET.format(status="closed", head="Acceptance", body="- [ ] x"))
        local = {"extra": "Ticket backend: local\nTicket root: tickets\n", "ledger": ledger}
        self.assertEqual(["Status in ticket [R-2](tickets/R-2.md)"], self.spine(**local)["missing"])
        (self.dir / "tickets/R-2.md").write_text(TICKET.format(status="Done", head="Acceptance", body="- [x] x"))
        self.assertTrue(self.spine(**local)["trackable"])
        (self.dir / "tickets/R-2.md").unlink()
        self.assertFalse(self.spine(**local)["trackable"])

    def test_ticket_files(self) -> None:
        for head in ("Acceptance", "Acceptance Criteria"):
            self.assertTrue(self.check(TICKET.format(status="ready", head=head, body="- [x] y"))["trackable"], head)
        result = self.check(TICKET.format(status="wip", head="Acceptance", body="prose"))
        self.assertEqual(["Status (draft/ready/active/blocked/done/deferred)", "checkbox under ## Acceptance Criteria"], result["missing"])
        self.assertEqual([], result["warnings"])
        self.assertFalse(self.check("# Notes\n\nJust text.\n")["trackable"])
        self.assertFalse(v.trackable(self.dir / "nope.md")["trackable"])

    def test_strict_failing_spine_is_trackable_and_does_not_crash(self) -> None:
        text = SPINE.format(**GOOD)
        path = self.dir / "s.md"
        path.write_text(text)
        self.assertTrue(v.validate_local(path).fails(strict=True))
        result = v.trackable(path)
        self.assertTrue(result["trackable"])
        self.assertTrue(result["warnings"])
        self.check("## Current State\n\n| broken\n|--\n## Issue Ledger\n\n| a |\n| b | c |\n")

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(VALIDATOR_PATH), "--trackable", *args], capture_output=True, text=True)

    def test_cli_text_and_json(self) -> None:
        good, bad = self.dir / "g.md", self.dir / "b.md"
        good.write_text(SPINE.format(**GOOD))
        bad.write_text(SPINE.format(**{**GOOD, "done": "none yet"}))
        done = self.run_cli(str(good))
        self.assertEqual((0, f"{good}: trackable\n"), (done.returncode, done.stdout))
        done = self.run_cli(str(good), str(bad))
        self.assertEqual(1, done.returncode)
        self.assertIn(f"{bad}: not trackable: checkbox under ## Definition Of Done", done.stdout)
        done = self.run_cli("--json", str(good), str(bad))
        data = json.loads(done.stdout)
        self.assertEqual([True, False], [d["trackable"] for d in data])
        self.assertEqual({"path", "trackable", "missing", "warnings"}, set(data[0]))
        self.assertEqual(["checkbox under ## Definition Of Done"], data[1]["missing"])


class PreCommitHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-hook-")
        self.repo = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.git("init", "-q")
        (self.repo / "docs").mkdir()
        (self.repo / "docs/EPIC.md").write_text("# Spine\n")

    def git(self, *args: str) -> subprocess.CompletedProcess:
        cmd = ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args]
        return subprocess.run(cmd, cwd=self.repo, capture_output=True, text=True)

    def install(self) -> None:
        agents_block.install(self.repo, "docs/EPIC.md")

    @property
    def hook(self) -> Path:
        return self.repo / ".git/hooks/pre-commit"

    def test_install_idempotent_and_uninstall_only_ours(self) -> None:
        self.install()
        text = self.hook.read_text()
        self.assertIn(agents_block.HOOK_MARK, text)
        self.assertTrue(self.hook.stat().st_mode & 0o111)
        self.install()
        self.assertEqual(text, self.hook.read_text())
        agents_block.uninstall(self.repo)
        self.assertFalse(self.hook.exists())
        self.hook.write_text("#!/bin/sh\necho foreign\n")
        agents_block.uninstall(self.repo)
        self.assertTrue(self.hook.exists())

    def test_foreign_hook_preserved(self) -> None:
        self.hook.write_text("#!/bin/sh\necho foreign\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.install()
        self.assertIn("foreign hook", out.getvalue())
        self.assertEqual("#!/bin/sh\necho foreign\n", self.hook.read_text())

    def test_respects_core_hooks_path(self) -> None:
        self.git("config", "core.hooksPath", "myhooks")
        self.install()
        self.assertTrue((self.repo / "myhooks/pre-commit").is_file())
        self.assertFalse(self.hook.exists())

    def test_non_git_dir_skips_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents_block.install(Path(tmp), "docs/EPIC.md")
            self.assertFalse((Path(tmp) / ".git").exists())

    def test_check_notes_missing_hook_without_failing(self) -> None:
        self.install()
        self.hook.unlink()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = agents_block.check(self.repo)
        self.assertIn("pre-commit trackable gate not installed", out.getvalue())
        self.assertEqual(0, code)

    def test_commit_gated_on_trackable_only(self) -> None:
        self.install()
        self.git("add", "-A")
        self.assertEqual(0, self.git("commit", "-m", "base").returncode)
        spine = self.repo / "docs/S.md"
        spine.write_text(SPINE.format(**{**GOOD, "done": "no checkboxes"}))
        self.git("add", "docs/S.md")
        blocked = self.git("commit", "-m", "bad")
        self.assertNotEqual(0, blocked.returncode)
        self.assertIn("not trackable: checkbox under ## Definition Of Done", blocked.stderr)
        spine.write_text(SPINE.format(**GOOD))  # trackable, but fails --strict
        self.git("add", "docs/S.md")
        allowed = self.git("commit", "-m", "good")
        self.assertEqual(0, allowed.returncode, allowed.stderr)
        self.assertIn("--strict issues (advisory", allowed.stderr)
        (self.repo / "notes.md").write_text("# plain\n")
        self.git("add", "notes.md")
        self.assertEqual(0, self.git("commit", "-m", "notes").returncode)


if __name__ == "__main__":
    unittest.main()
