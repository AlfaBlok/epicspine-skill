from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_agents_block import agents_block
from test_validate_spine import validate_spine as v, VALIDATOR_PATH

sys.path.insert(0, str(VALIDATOR_PATH.parent))
import spine_fix  # noqa: E402

ASSETS = VALIDATOR_PATH.parents[1] / "assets"

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
GOOD = {"extra": "", "status": "active — building", "done": "- [ ] X-1 ship", "ledger": LEDGER}


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
        self.assertTrue(self.spine(done="- [x] A-1 a\n- [X] M4-2 b — evidence note")["trackable"])
        result = self.spine(done="Prose only.")
        self.assertEqual(["criteria `- [ ] ID text` under ## Definition Of Done"], result["missing"])
        self.assertFalse(self.spine(done="* [ ] A-1 bullet")["trackable"])

    def test_id_rule(self) -> None:
        for bad in ("- [ ] ship", "- [ ] 1. ship", "- [ ] m4-1 ship", "- [ ] M4 ship", "- [ ] M4-1: ship", "- A-1 ship", "1. A-1 ship"):
            result = self.spine(done=f"- [ ] OK-1 fine\n{bad}")
            self.assertEqual(["1 criteria under ## Definition Of Done not `- [ ] ID text` (lines 13)"], result["missing"], bad)
        self.assertTrue(self.spine(done="- [ ] X-1 a\n- [ ] Z9-10 b\n- [ ] A1B-2")["trackable"])

    def test_duplicate_ids(self) -> None:
        self.assertEqual(["duplicate criterion IDs: X-1"], self.spine(done="- [ ] X-1 a\n- [x] X-1 b\n- [ ] X-2 c")["missing"])

    def test_continuations_and_prose_are_not_criteria(self) -> None:
        done = ("SHIP — one journey.\n\n<!-- one\n- not a criterion\n-->\nAcceptance outcome: x\n\n"
                "- [ ] X-1 first\n  indented continuation\n  - nested bullet\n\nHARDEN — later:\n\n- [ ] X-2 second <!-- note -->\n```\n- fenced\n```")
        self.assertTrue(self.spine(done=done)["trackable"])

    def test_aliases_need_the_canonical_heading_for_spines(self) -> None:
        for head in ("Exit Test", "Exit Test (Definition Of Done)", "Acceptance", "Definition of Done"):
            text = SPINE.format(**GOOD).replace("## Definition Of Done", f"## {head}")
            self.assertEqual([f"heading '## {head}' must be '## Definition Of Done'"], self.check(text)["missing"], head)

    def test_templates_stay_trackable(self) -> None:
        for name, heads, count in (("epic-spine-template.md", ("Definition Of Done",), 6), ("compact-spine-template.md", ("Definition Of Done",), 1),
                                   ("github-issue-template.md", ("Acceptance Criteria",), 3)):
            items = v.criteria((ASSETS / name).read_text(encoding="utf-8"), heads)
            self.assertEqual(count, len(items), name)
            self.assertTrue(all(v.CRITERION_RE.match(line) for _, line in items), name)

    def test_ledger_needs_status_column_but_may_be_absent(self) -> None:
        bad = "| Issue | Title | Owner |\n|---|---|---|\n| draft | A | me |"
        self.assertEqual(["Issue Ledger Status column"], self.spine(ledger=bad)["missing"])
        text = SPINE.format(**GOOD).split("## Issue Ledger")[0]
        self.assertTrue(self.check(text)["trackable"])

    def test_local_backend_checks_ticket_files(self) -> None:
        ledger = "| Ticket | Depends On |\n|---|---|\n| [R-1](tickets/R-1.md) | none |\n| [R-2](tickets/R-2.md) | none |"
        (self.dir / "tickets").mkdir()
        (self.dir / "tickets/R-1.md").write_text(TICKET.format(status="ready", head="Acceptance", body="- [ ] AC-1 x"))
        (self.dir / "tickets/R-2.md").write_text(TICKET.format(status="closed", head="Acceptance", body="- [ ] AC-1 x"))
        local = {"extra": "Ticket backend: local\nTicket root: tickets\n", "ledger": ledger}
        self.assertEqual(["Status in ticket [R-2](tickets/R-2.md)"], self.spine(**local)["missing"])
        (self.dir / "tickets/R-2.md").write_text(TICKET.format(status="Done", head="Acceptance", body="- [x] AC-1 x"))
        self.assertTrue(self.spine(**local)["trackable"])
        (self.dir / "tickets/R-2.md").unlink()
        self.assertFalse(self.spine(**local)["trackable"])

    def test_ticket_files(self) -> None:
        for head in ("Acceptance", "Acceptance Criteria"):
            self.assertTrue(self.check(TICKET.format(status="ready", head=head, body="- [x] AC-1 y"))["trackable"], head)
        result = self.check(TICKET.format(status="wip", head="Acceptance", body="prose"))
        self.assertEqual(["Status is not draft/ready/active/blocked/done/deferred (got 'wip')", "criteria `- [ ] ID text` under ## Acceptance Criteria/Acceptance"], result["missing"])
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
        self.assertIn(f"{bad}: not trackable: criteria `- [ ] ID text` under ## Definition Of Done", done.stdout)
        done = self.run_cli("--json", str(good), str(bad))
        data = json.loads(done.stdout)
        self.assertEqual([True, False], [d["trackable"] for d in data])
        self.assertEqual({"path", "trackable", "missing", "warnings"}, set(data[0]))
        self.assertEqual(["criteria `- [ ] ID text` under ## Definition Of Done"], data[1]["missing"])


class FixTests(unittest.TestCase):
    def fix(self, text: str) -> tuple[str, list[str]]:
        return spine_fix.fix_text(text)

    def spine(self, done: str, status: str = "active", head: str = "Definition Of Done") -> str:
        return SPINE.format(**{**GOOD, "done": done, "status": status}).replace("## Definition Of Done", f"## {head}")

    def test_criteria_forms_are_rewritten_with_text_unchanged(self) -> None:
        done = "Intro prose.\n\n1. one\n2) two\n- bullet\n* star\n- [ ] unchecked\n- [x] 7. ticked — proof\n  continuation\n\nHARDEN — later:"
        new, what = self.fix(self.spine(done))
        self.assertEqual("Intro prose.\n\n- [ ] DOD-1 one\n- [ ] DOD-2 two\n- [ ] DOD-3 bullet\n- [ ] DOD-4 star\n- [ ] DOD-5 unchecked\n"
                         "- [x] DOD-6 ticked — proof\n  continuation\n\nHARDEN — later:", new.split("## Definition Of Done\n\n")[1].split("\n\n## Issue")[0])
        self.assertEqual(["6 criteria -> '- [ ] ID text'"], what)

    def test_existing_ids_kept_and_prefix_inferred(self) -> None:
        new, _ = self.fix(self.spine("- [x] M4-2 keep\n- [ ] M4-7 keep\n- [ ] M2-1 other\n- plain\n- M4-3: reformat\n- **M4-9** bold\n- [ ] fresh"))
        body = new.split("## Definition Of Done\n\n")[1].split("\n\n## Issue")[0].split("\n")
        self.assertEqual(["- [x] M4-2 keep", "- [ ] M4-7 keep", "- [ ] M2-1 other", "- [ ] M4-10 plain", "- [ ] M4-3 reformat", "- [ ] M4-9 bold", "- [ ] M4-11 fresh"], body)
        self.assertIn("\n- [ ] AC-1 one\n", self.fix(TICKET.format(status="ready", head="Acceptance", body="- one"))[0])

    def test_idempotent_and_trackable_after(self) -> None:
        once, _ = self.fix(self.spine("1. a\n- b", status="In progress", head="Exit Test (DoD)"))
        self.assertEqual((once, []), self.fix(once))
        path = Path(tempfile.mkdtemp()) / "s.md"
        path.write_text(once)
        self.assertTrue(v.trackable(path)["trackable"])

    def test_heading_rename_only_without_canonical_section(self) -> None:
        for head in ("Exit Test (DoD)", "Acceptance"):
            new, what = self.fix(self.spine("- [ ] A-1 a", head=head))
            self.assertIn("## Definition Of Done\n", new)
            self.assertEqual([f"heading '{head}' -> Definition Of Done"], what)
        both = self.spine("- [ ] A-1 a").replace("## Issue Ledger", "## Acceptance\n\n- extra\n\n## Issue Ledger")
        self.assertEqual(both, self.fix(both)[0])

    def test_status_synonyms(self) -> None:
        cases = {"in progress": "active", "In-Progress — x": "active", "wip": "active", "Doing": "active", "review": "active", "testing": "active",
                 "todo": "ready", "To Do": "ready", "planned": "ready", "open": "ready", "backlog": "ready",
                 "CLOSED": "done", "complete": "done", "Completed.": "done", "shipped": "done", "merged": "done",
                 "on hold": "deferred", "paused": "deferred", "parked": "deferred"}
        for old, want in cases.items():
            new, what = self.fix(self.spine("- [ ] A-1 a", status=old))
            self.assertIn(f"\nStatus: {want}", new, old)
            self.assertEqual(1, len(what), old)
        self.assertIn("Status: active — x", self.fix(self.spine("- [ ] A-1 a", status="In-Progress — x"))[0])

    def test_unknown_status_untouched_and_nothing_invented(self) -> None:
        text = self.spine("- [ ] A-1 a", status="planning").replace("Status: planning", "Status: planning")
        self.assertEqual((text, []), self.fix(text))
        no_status = self.spine("- [ ] A-1 a").replace("Status: active\n", "")
        self.assertEqual((no_status, []), self.fix(no_status))
        empty = self.spine("Prose only.")
        self.assertEqual((empty, []), self.fix(empty))
        no_column = self.spine("- [ ] A-1 a").replace("| Status", "| State")
        self.assertEqual((no_column, []), self.fix(no_column))
        self.assertEqual(("# Notes\n\nStatus: wip\n- a\n", []), self.fix("# Notes\n\nStatus: wip\n- a\n"))

    def test_ledger_and_ticket_status_cells(self) -> None:
        text = self.spine("- [ ] A-1 a").replace("| draft | A | me | draft |", "| a | A | me | In Progress |\n| b | B | me | weird |\n| c | C | me | review: waiting |")
        new, what = self.fix(text)
        self.assertIn("| a | A | me | active |\n| b | B | me | weird |\n| c | C | me | review: waiting |", new)
        self.assertEqual(["ledger Status 'In Progress' -> active"], what)
        new, what = self.fix(TICKET.format(status="Closed", head="Acceptance", body="1. done it"))
        self.assertIn("Status: done\n", new)
        self.assertIn("- [ ] AC-1 done it", new)

    def test_cli_fix_in_place(self) -> None:
        path = Path(tempfile.mkdtemp()) / "s.md"
        path.write_text(self.spine("- a", status="open"))
        done = subprocess.run([sys.executable, "-B", str(VALIDATOR_PATH), "--fix", str(path)], capture_output=True, text=True)
        self.assertEqual(0, done.returncode)
        self.assertIn(f"{path}: fixed: 1 criteria -> '- [ ] ID text'; Status 'open' -> ready", done.stdout)
        self.assertTrue(v.trackable(path)["trackable"])
        again = subprocess.run([sys.executable, "-B", str(VALIDATOR_PATH), "--fix", str(path)], capture_output=True, text=True)
        self.assertIn("nothing to fix", again.stdout)


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
        self.assertIn("not trackable: criteria `- [ ] ID text` under ## Definition Of Done", blocked.stderr)
        spine.write_text(SPINE.format(**GOOD))  # trackable, but fails --strict
        self.git("add", "docs/S.md")
        allowed = self.git("commit", "-m", "good")
        self.assertEqual(0, allowed.returncode, allowed.stderr)
        self.assertIn("--strict issues (advisory", allowed.stderr)
        (self.repo / "notes.md").write_text("# plain\n")
        self.git("add", "notes.md")
        self.assertEqual(0, self.git("commit", "-m", "notes").returncode)

    def commit(self, name: str, text: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
        (self.repo / name).write_text(text)
        self.git("add", name)
        cmd = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-m", "x"]
        return subprocess.run(cmd, cwd=cwd or self.repo, capture_output=True, text=True)

    def test_auto_fix_commits_compliant_text(self) -> None:
        self.install()
        sub = self.repo / "docs"
        done = self.commit("docs/S.md", SPINE.format(**{**GOOD, "done": "1. ship\n- verify", "status": "in progress"}), cwd=sub)
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("epicspine: fixed docs/S.md: 2 criteria -> '- [ ] ID text'; Status 'in progress' -> active", done.stderr)
        committed = self.git("show", "HEAD:docs/S.md").stdout
        self.assertIn("- [ ] DOD-1 ship\n- [ ] DOD-2 verify", committed)
        self.assertIn("Status: active", committed)
        self.assertEqual(committed, (self.repo / "docs/S.md").read_text())
        self.assertNotIn("docs/S.md", self.git("status", "--porcelain").stdout)

    def test_partially_staged_file_is_not_touched_and_blocks_with_command(self) -> None:
        self.install()
        path = self.repo / "docs/S.md"
        path.write_text(SPINE.format(**{**GOOD, "done": "- ship"}))
        self.git("add", "docs/S.md")
        path.write_text(path.read_text() + "\nunstaged edit\n")
        before = path.read_text()
        blocked = self.git("commit", "-m", "x")
        self.assertNotEqual(0, blocked.returncode)
        self.assertEqual(before, path.read_text())
        self.assertIn("unstaged changes", blocked.stderr)
        self.assertIn("validate_spine.py --fix docs/S.md", blocked.stderr)

    def test_missing_status_blocks_with_hint(self) -> None:
        self.install()
        blocked = self.commit("docs/S.md", SPINE.format(**{**GOOD, "status": "x"}).replace("Status: x\n", ""))
        self.assertNotEqual(0, blocked.returncode)
        self.assertIn("Current State Status missing: draft/ready/active/blocked/done/deferred", blocked.stderr)
        self.assertNotIn("epicspine: fixed", blocked.stderr)

    def test_fix_leaving_it_untrackable_still_blocks(self) -> None:
        self.install()
        blocked = self.commit("docs/S.md", SPINE.format(**{**GOOD, "status": "planning", "done": "- ship"}))
        self.assertNotEqual(0, blocked.returncode)
        self.assertIn("epicspine: fixed docs/S.md: 1 criteria", blocked.stderr)
        self.assertIn("Current State Status is not draft/ready/active/blocked/done/deferred (got 'planning')", blocked.stderr)
        self.assertNotIn("criteria `", blocked.stderr)


class SessionStartInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-session-")
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.cwd = os.getcwd()
        self.addCleanup(os.chdir, self.cwd)
        self.env = {"CLAUDE_CONFIG_DIR": str(self.root / "cfg")}

    def repo(self, name: str, agents: str | None) -> Path:
        path = self.root / name
        path.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=path, check=True)
        if agents is not None:
            (path / "AGENTS.md").write_text(agents)
        return path

    def payload(self, cwd: Path) -> None:
        os.chdir(cwd)
        self.assertIn("hookSpecificOutput", json.loads(agents_block.global_install.hook_payload(self.env)))

    def test_installs_hook_in_epicspine_repo_not_elsewhere(self) -> None:
        block = agents_block.render("docs/EPIC.md")
        for name, agents in (("block", block), ("rootline", "Root spine: [`EPIC.md`](EPIC.md).\n")):
            repo = self.repo(name, agents)
            (repo / "EPIC.md").write_text("# e\n")
            self.payload(repo)
            self.assertIn(agents_block.HOOK_MARK, (repo / ".git/hooks/pre-commit").read_text(), name)
        plain = self.repo("plain", "# just a readme\n")
        self.payload(plain)
        self.assertFalse((plain / ".git/hooks/pre-commit").exists())
        self.payload(self.repo("noagents", None))
        self.assertFalse((self.root / "noagents/.git/hooks/pre-commit").exists())

    def test_subdirectory_foreign_hook_and_failures_are_harmless(self) -> None:
        repo = self.repo("r", agents_block.render("docs/EPIC.md"))
        (repo / "sub").mkdir()
        foreign = repo / ".git/hooks/pre-commit"
        foreign.write_text("#!/bin/sh\necho foreign\n")
        self.payload(repo / "sub")
        self.assertEqual("#!/bin/sh\necho foreign\n", foreign.read_text())
        foreign.unlink()
        self.payload(repo / "sub")
        self.assertTrue(foreign.is_file())
        self.payload(self.root)  # not a git repo
        os.chdir(repo)
        with mock.patch("subprocess.run", side_effect=OSError("no git")):
            agents_block.global_install.heal_repo()


if __name__ == "__main__":
    unittest.main()
