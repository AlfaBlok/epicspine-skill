"""SessionStart self-sync: skill, dispatch profile, current repo, repo self-install. Local git only, no network."""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import agents_block as ab  # noqa: E402
import global_install  # noqa: E402
import rehook  # noqa: E402
import repo_sync  # noqa: E402
import stop_push  # noqa: E402
import session_sync as ss  # noqa: E402
import skill_update as su  # noqa: E402
from test_validate_spine import validate_spine as v  # noqa: E402

GIT_ENV = {"GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "T",
           "GIT_COMMITTER_EMAIL": "t@example.com", "GIT_TERMINAL_PROMPT": "0"}
SPINE = ("# EPIC: Demo\n\nSpine ID: demo\nSpine Type: root\nRoot spine: self\nParent spine: none\n"
         "Integration branch: main\n\n## Mission\nx\n\n## Current State\nStatus: active\n\n## Definition Of Done\n"
         "- [ ] D-1 works\n")


def git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True,
                          env={**os.environ, **GIT_ENV})
    return proc.stdout.strip()


def commit(cwd: Path, name: str, text: str, msg: str | None = None) -> None:
    path = cwd / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(cwd, "add", "-A")
    git(cwd, "commit", "-qm", msg or f"edit {name}")


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-sync-")
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.clock = ss.Clock(30)

    def remote_and_clone(self, name: str, seed: dict[str, str] | None = None) -> tuple[Path, Path]:
        """A bare origin plus one clone seeded with ``seed`` on branch main."""
        bare, clone = self.tmp / f"{name}.git", self.tmp / name
        git(self.tmp, "init", "-q", "--bare", "-b", "main", str(bare))
        git(self.tmp, "clone", "-q", str(bare), str(clone))
        git(clone, "checkout", "-q", "-B", "main")
        for rel, text in (seed or {"README.md": "x\n"}).items():
            commit(clone, rel, text)
        git(clone, "push", "-q", "-u", "origin", "main")
        return bare, clone

    def second_clone(self, bare: Path, name: str) -> Path:
        other = self.tmp / name
        git(self.tmp, "clone", "-q", str(bare), str(other))
        return other


class ThrottleAndProfileTest(Base):
    def test_due_once_per_ten_minutes(self) -> None:
        home = self.tmp / "h"
        self.assertTrue(ss.due(home, now=1000.0))
        self.assertFalse(ss.due(home, now=1000.0 + ss.THROTTLE_SECONDS - 1))
        self.assertTrue(ss.due(home, now=1000.0 + ss.THROTTLE_SECONDS + 1))

    def test_profile_synced_from_canonical_and_idempotent(self) -> None:
        home = self.tmp / "h"
        target = home / ".agents" / "epicspine-profile.md"
        target.parent.mkdir(parents=True)
        target.write_text("Dispatch profile: opencode_2 DeepSeek\n")  # the stale Mac file
        self.assertEqual(ss.sync_profile(home), "dispatch profile synced")
        self.assertEqual(target.read_text(), ss.CANONICAL_PROFILE.read_text())
        self.assertIn("claude-sonnet-5-5", target.read_text())
        self.assertIsNone(ss.sync_profile(home))

    def test_local_override_is_never_overwritten(self) -> None:
        home = self.tmp / "h"
        (home / ".agents").mkdir(parents=True)
        (home / ".agents" / "epicspine-profile.local.md").write_text("Dispatch profile: mine\n")
        self.assertIsNone(ss.sync_profile(home))
        self.assertFalse((home / ".agents" / "epicspine-profile.md").exists())

    def test_missing_canonical_changes_nothing(self) -> None:
        home = self.tmp / "h"
        self.assertIsNone(ss.sync_profile(home, canonical=self.tmp / "nope.md"))
        self.assertFalse(home.exists())

    def test_canonical_profile_is_a_dispatch_profile_line(self) -> None:
        self.assertTrue(ss.CANONICAL_PROFILE.read_text().startswith("Dispatch profile: "))


class SkillSyncTest(Base):
    def skill_repo(self, version: str = "1") -> tuple[Path, Path]:
        return self.remote_and_clone("src", {"skill/epic-spine/VERSION": version + "\n", "README.md": "x\n"})

    def test_checkout_fast_forwards_and_reports_versions(self) -> None:
        bare, clone = self.skill_repo()
        git(self.second_clone(bare, "dev"), "status")
        dev = self.tmp / "dev"
        commit(dev, "skill/epic-spine/VERSION", "2\n")
        git(dev, "push", "-q", "origin", "main")
        skill = clone / "skill" / "epic-spine"
        self.assertEqual(ss.sync_checkout(skill.resolve(), self.clock), "skill 1 -> 2")
        self.assertEqual((skill / "VERSION").read_text(), "2\n")
        self.assertIsNone(ss.sync_checkout(skill.resolve(), self.clock))  # now current

    def test_checkout_leaves_dirty_ahead_and_diverged_trees_alone(self) -> None:
        bare, clone = self.skill_repo()
        dev = self.second_clone(bare, "dev")
        commit(dev, "skill/epic-spine/VERSION", "2\n")
        git(dev, "push", "-q", "origin", "main")
        skill = (clone / "skill" / "epic-spine").resolve()
        (skill / "VERSION").write_text("local edit\n")
        self.assertIsNone(ss.sync_checkout(skill, self.clock))  # dirty
        self.assertEqual((skill / "VERSION").read_text(), "local edit\n")
        git(clone, "checkout", "--", ".")
        commit(clone, "other.txt", "mine")
        self.assertIsNone(ss.sync_checkout(skill, self.clock))  # diverged
        self.assertEqual((skill / "VERSION").read_text(), "1\n")

    def test_vendored_copy_and_no_origin_are_left_alone(self) -> None:
        bare, clone = self.remote_and_clone("host", {"vendor/epic-spine/VERSION": "1\n"})
        self.assertIsNone(ss.sync_checkout((clone / "vendor" / "epic-spine").resolve(), self.clock))
        lone = self.tmp / "lone"
        git(self.tmp, "init", "-q", "-b", "main", str(lone))
        commit(lone, "skill/epic-spine/VERSION", "1\n")
        self.assertIsNone(ss.sync_checkout((lone / "skill" / "epic-spine").resolve(), self.clock))

    def pinned(self) -> tuple[Path, Path]:
        """A source repo (with MANIFEST) and an installed pinned copy of its first commit."""
        src = self.tmp / "psrc"
        skill = src / "skill" / "epic-spine"
        skill.mkdir(parents=True)
        (skill / "VERSION").write_text("1\n")
        (src / "MANIFEST.sha256").write_text(su.generate_manifest(src))
        git(self.tmp, "init", "-q", "-b", "main", str(src))
        git(src, "add", "-A")
        git(src, "commit", "-qm", "one")
        installed = self.tmp / "skills" / "epic-spine"
        installed.parent.mkdir()
        subprocess.run(["cp", "-r", str(skill), str(installed)], check=True)
        tree, head = git(src, "rev-parse", "HEAD:skill/epic-spine"), git(src, "rev-parse", "HEAD")
        (installed.parent / "epic-spine.SOURCE").write_text(
            f"source: {src}\npath: skill/epic-spine\ncommit: {head}\nmanifest: {'0' * 64}\nversion: 1\n"
            f"installed: 2026-01-01\nchecked: 2026-01-01\ntree: {tree}\nlatest: {tree}\n")
        return src, installed

    def test_pinned_copy_upgrades_when_remote_moved(self) -> None:
        src, installed = self.pinned()
        with mock.patch.object(sys.modules["skill_update"], "skill_dir_from_here", return_value=installed):
            self.assertIsNone(ss.sync_pinned(installed, self.clock))  # same commit: nothing to do
            (src / "skill/epic-spine/VERSION").write_text("2\n")
            (src / "MANIFEST.sha256").write_text(su.generate_manifest(src))
            git(src, "add", "-A")
            git(src, "commit", "-qm", "two")
            self.assertEqual(ss.sync_pinned(installed, self.clock), "skill 1 -> 2")
        self.assertEqual((installed / "VERSION").read_text(), "2\n")

    def test_vendored_pin_is_never_upgraded(self) -> None:
        src, installed = self.pinned()
        (installed.parent / "epic-spine.SOURCE").write_text("source: x\nmanifest: not-a-digest\n")
        with mock.patch.object(sys.modules["skill_update"], "skill_dir_from_here", return_value=installed):
            self.assertIsNone(ss.sync_pinned(installed, self.clock))
        self.assertEqual((installed / "VERSION").read_text(), "1\n")

    def test_skill_updates_off_or_manual_skips(self) -> None:
        for value, blocked in (("off", True), ("manual", True), ("auto", False)):
            repo = self.tmp / f"r-{value}"
            repo.mkdir()
            (repo / "AGENTS.md").write_text(f"Skill updates: {value}\n")
            self.assertEqual(ss.skills_blocked(repo), blocked)
        self.assertFalse(ss.skills_blocked(self.tmp / "none"))


class RunTest(Base):
    def run_sync(self, env: dict | None = None, **kw) -> list[str]:
        return ss.run(env or {}, home=self.tmp / "home", cwd=self.tmp, clock=self.clock, **kw)

    def test_off_switch_does_nothing(self) -> None:
        with mock.patch.object(ss, "sync_skill", side_effect=AssertionError("must not run")):
            self.assertEqual(self.run_sync({"EPICSPINE_SYNC": "off"}), [])
        self.assertFalse((self.tmp / "home").exists())

    def test_one_line_reports_skill_and_profile(self) -> None:
        with mock.patch.object(ss, "sync_skill", return_value="skill 2026.10.16.3 -> 2026.10.16.4"):
            notes = self.run_sync()
        self.assertEqual(notes, ["EpicSpine sync: skill 2026.10.16.3 -> 2026.10.16.4; dispatch profile synced"])
        with mock.patch.object(ss, "sync_skill", return_value="again"):
            self.assertEqual(self.run_sync(), [])  # throttled + profile current

    def test_never_raises(self) -> None:
        with mock.patch.object(ss, "sync_skill", side_effect=RuntimeError("boom")), \
                mock.patch.object(ss, "sync_profile", side_effect=RuntimeError("boom")), \
                mock.patch.object(repo_sync, "run", side_effect=RuntimeError("boom")):
            self.assertEqual(self.run_sync(), [])

    def test_expired_clock_skips_git_work(self) -> None:
        gone = ss.Clock(-1)
        self.assertIsNone(ss.git(["--version"], self.tmp, gone))


class RepoSyncTest(Base):
    def setUp(self) -> None:
        super().setUp()
        self.bare, self.repo = self.remote_and_clone("proj", {"docs/EPIC.md": SPINE, "AGENTS.md": "Integration policy: main-direct\n"})
        self.dev = self.second_clone(self.bare, "dev")

    def push_from_dev(self, name: str = "dev.txt") -> None:
        commit(self.dev, name, "d")
        git(self.dev, "push", "-q", "origin", "main")

    def sync(self) -> list[str]:
        return repo_sync.sync(self.repo, self.clock)

    def test_clean_and_behind_fast_forwards(self) -> None:
        self.push_from_dev()
        self.assertEqual(self.sync(), ["EpicSpine sync: repo proj main fast-forwarded 1 commit(s)"])
        self.assertTrue((self.repo / "dev.txt").exists())
        self.assertEqual(self.sync(), [])

    def test_dirty_and_behind_on_integration_branch_asks_the_user(self) -> None:
        self.push_from_dev()
        (self.repo / "AGENTS.md").write_text("changed\n")
        (note,) = self.sync()
        self.assertTrue(note.startswith("EpicSpine attention: repo proj (main) needs the user: 1 commit(s) behind"))
        self.assertIn("uncommitted", note)
        self.assertFalse((self.repo / "dev.txt").exists())
        self.assertEqual((self.repo / "AGENTS.md").read_text(), "changed\n")

    def test_diverged_changes_nothing_and_says_so(self) -> None:
        self.push_from_dev()
        commit(self.repo, "mine.txt", "m")
        head = git(self.repo, "rev-parse", "HEAD")
        (note,) = self.sync()
        self.assertIn("diverged from origin/main (1 ahead, 1 behind)", note)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head)

    def test_ahead_on_integration_branch_is_pushed_fast_forward_only(self) -> None:
        commit(self.repo, "mine.txt", "m")
        self.assertEqual(self.sync(), ["EpicSpine sync: repo proj pushed 1 commit(s) to origin/main"])
        self.assertEqual(git(self.bare, "rev-parse", "main"), git(self.repo, "rev-parse", "HEAD"))

    def test_pr_approval_policy_blocks_the_push(self) -> None:
        commit(self.repo, "AGENTS.md", "Integration policy: pr-approval\n")
        (note,) = self.sync()
        self.assertIn("pr-approval", note)
        self.assertNotEqual(git(self.bare, "rev-parse", "main"), git(self.repo, "rev-parse", "HEAD"))

    def test_failed_push_is_reported_not_forced(self) -> None:
        commit(self.repo, "mine.txt", "m")
        hook = self.bare / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        (note,) = self.sync()
        self.assertIn("push failed", note)

    def test_feature_branch_ahead_or_diverged_is_ignored(self) -> None:
        git(self.repo, "checkout", "-q", "-b", "feat/x")
        git(self.repo, "push", "-q", "-u", "origin", "feat/x")
        commit(self.repo, "f.txt", "f")
        self.assertEqual(self.sync(), [])
        self.assertNotIn("f.txt", git(self.bare, "ls-tree", "--name-only", "-r", "feat/x"))

    def test_unrelated_states_are_silent(self) -> None:
        git(self.repo, "checkout", "-q", "--detach")
        self.assertEqual(self.sync(), [])  # detached
        git(self.repo, "checkout", "-q", "main")
        git(self.repo, "remote", "set-url", "origin", str(self.tmp / "gone.git"))
        self.assertEqual(self.sync(), [])  # offline / unreachable
        git(self.repo, "remote", "remove", "origin")
        self.assertEqual(self.sync(), [])  # no origin
        self.assertEqual(repo_sync.run(self.tmp / "not-a-repo", self.clock), [])

    def test_mid_merge_state_is_left_alone(self) -> None:
        self.push_from_dev()
        (Path(git(self.repo, "rev-parse", "--absolute-git-dir")) / "MERGE_HEAD").write_text("0" * 40 + "\n")
        self.assertEqual(self.sync(), [])
        self.assertFalse((self.repo / "dev.txt").exists())


class RepoInstallTest(Base):
    def repo(self, files: dict[str, str]) -> Path:
        repo = self.tmp / "r"
        git(self.tmp, "init", "-q", "-b", "main", str(repo))
        for rel, text in files.items():
            commit(repo, rel, text)
        return repo

    def test_spine_without_block_gets_block_and_learnings_uncommitted(self) -> None:
        legacy = SPINE.replace("Spine ID: demo\nSpine Type: root\nRoot spine: self\nParent spine: none\n", "Primary document: `docs/EPIC_SPINE.md`\n")
        repo = self.repo({"docs/EPIC_SPINE.md": legacy, "README.md": "x\n"})  # abnb-agent shape
        (note,) = repo_sync.install(repo, self.clock)
        self.assertIn("AGENTS.md block and Operating Learnings in docs/EPIC_SPINE.md", note)
        self.assertIn("uncommitted", note)
        self.assertEqual(ab.check(repo), 0)
        self.assertIn("Root spine: docs/EPIC_SPINE.md.", (repo / "AGENTS.md").read_text())
        text = (repo / "docs/EPIC_SPINE.md").read_text()
        self.assertLess(text.index("## Operating Learnings"), text.index("## Current State"))
        self.assertIn("**Always**", text)
        self.assertIn("**Scoped index**", text)
        self.assertEqual(git(repo, "status", "--porcelain").count("\n"), 1)  # AGENTS.md + spine changed: 2 lines
        self.assertEqual(repo_sync.install(repo, self.clock), [])  # idempotent

    def test_installed_section_keeps_the_spine_valid(self) -> None:
        repo = self.repo({"docs/EPIC.md": SPINE})
        before = v.validate_local(repo / "docs/EPIC.md")
        repo_sync.install(repo, self.clock)
        after = v.validate_local(repo / "docs/EPIC.md")
        self.assertEqual(after.errors, before.errors)
        self.assertEqual(sorted(set(after.warnings) - set(before.warnings)), [])
        self.assertIn("Operating Learnings", after.sections)

    def test_existing_learnings_section_and_current_block_untouched(self) -> None:
        spine = SPINE.replace("## Current State", "## Operating Learnings\n\n- L-1 | any | do x | why | confirmed 2026-10-01\n\n## Current State")
        repo = self.repo({"docs/EPIC.md": spine})
        ab.install(repo, "docs/EPIC.md")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "setup")
        self.assertEqual(repo_sync.install(repo, self.clock), [])
        self.assertEqual(git(repo, "status", "--porcelain"), "")

    def test_stale_block_is_refreshed(self) -> None:
        repo = self.repo({"docs/EPIC.md": SPINE, "AGENTS.md": "# Mine\n\n<!-- epicspine:begin old -->\nRoot spine: docs/EPIC.md. Read its\n<!-- epicspine:end -->\n"})
        (note,) = repo_sync.install(repo, self.clock)
        self.assertIn("AGENTS.md block", note)
        self.assertEqual(ab.check(repo), 0)
        self.assertIn("# Mine", (repo / "AGENTS.md").read_text())

    def test_repo_without_a_spine_gets_a_none_block_when_it_has_an_origin(self) -> None:
        repo = self.repo({"README.md": "x\n", "AGENTS.md": "# Mine\n"})
        self.assertEqual(repo_sync.install(repo, self.clock), [])  # no origin: left alone
        self.assertEqual((repo / "AGENTS.md").read_text(), "# Mine\n")
        git(repo, "remote", "add", "origin", str(self.tmp / "nowhere.git"))
        (note,) = repo_sync.install(repo, self.clock)
        self.assertIn("AGENTS.md block (Root spine: none)", note)
        text = (repo / "AGENTS.md").read_text()
        self.assertTrue(text.startswith("# Mine"))
        self.assertIn("Root spine: none. Read the README's first screen before acting.", text)
        self.assertEqual(ab.check(repo), 0)
        self.assertEqual(repo_sync.install(repo, self.clock), [])  # idempotent
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ab.profile(repo, self.tmp / "nohome", None), 3)  # `none` is not read as a spine path

    def test_epic_without_current_state_counts_as_no_spine(self) -> None:
        repo = self.repo({"EPIC.md": "# EPIC: Poly\n\n## Mission\nx\n"})  # poly-maker shape
        git(repo, "remote", "add", "origin", str(self.tmp / "nowhere.git"))
        (note,) = repo_sync.install(repo, self.clock)
        self.assertIn("(Root spine: none)", note)
        self.assertEqual(ab.check(repo), 0)

    def test_none_block_upgrades_when_a_spine_appears(self) -> None:
        repo = self.repo({"README.md": "x\n"})
        git(repo, "remote", "add", "origin", str(self.tmp / "nowhere.git"))
        repo_sync.install(repo, self.clock)
        commit(repo, "docs/EPIC.md", SPINE)
        (note,) = repo_sync.install(repo, self.clock)
        self.assertIn("AGENTS.md block and Operating Learnings in docs/EPIC.md", note)
        self.assertIn("Root spine: docs/EPIC.md. Read its Current State", (repo / "AGENTS.md").read_text())

    def test_ambiguous_spines_get_a_none_block_and_a_question(self) -> None:
        legacy = SPINE.replace("Spine Type: root\n", "")
        repo = self.repo({"docs/EPIC-A.md": legacy, "docs/EPIC-B.md": legacy})
        git(repo, "remote", "add", "origin", str(self.tmp / "nowhere.git"))
        first = repo_sync.install(repo, self.clock)
        self.assertIn("(Root spine: none)", first[0])
        self.assertTrue(first[1].startswith("EpicSpine attention:") and "docs/EPIC-A.md, docs/EPIC-B.md" in first[1])
        self.assertIn("--root-spine", first[1])
        again = repo_sync.install(repo, self.clock)  # asked every session until the user decides
        self.assertEqual(len(again), 1)
        self.assertTrue(again[0].startswith("EpicSpine attention:"))

    def test_opt_out_skips_install_and_sync(self) -> None:
        for marker in (".epicspine-off", "AGENTS.md"):
            repo = self.tmp / marker.strip(".")
            git(self.tmp, "init", "-q", "-b", "main", str(repo))
            commit(repo, "docs/EPIC.md", SPINE)
            git(repo, "remote", "add", "origin", str(self.tmp / "nowhere.git"))
            (repo / marker).write_text("EpicSpine: off\n" if marker == "AGENTS.md" else "")
            self.assertTrue(repo_sync.opted_out(repo))
            self.assertEqual(repo_sync.run(repo, self.clock), [])
            self.assertEqual((repo / "AGENTS.md").read_text() if (repo / "AGENTS.md").exists() else "", "EpicSpine: off\n" if marker == "AGENTS.md" else "")

    def test_worktree_is_left_to_the_primary_checkout(self) -> None:
        repo = self.repo({"README.md": "x\n"})
        git(repo, "remote", "add", "origin", str(self.tmp / "nowhere.git"))
        git(repo, "worktree", "add", "-q", str(self.tmp / "wt"), "-b", "wt/x")
        self.assertEqual(repo_sync.install(self.tmp / "wt", self.clock), [])
        self.assertFalse((self.tmp / "wt" / "AGENTS.md").exists())

    def test_child_and_ambiguous_spines_are_not_guessed(self) -> None:
        child = SPINE.replace("Spine Type: root", "Spine Type: child").replace("Root spine: self", "Root spine: docs/EPIC.md")
        repo = self.repo({"docs/EPIC.md": SPINE, "docs/EPIC-1-CHILD.md": child})
        self.assertEqual(repo_sync.find_spine(repo, self.clock), repo / "docs/EPIC.md")
        two = self.tmp / "two"
        git(self.tmp, "init", "-q", "-b", "main", str(two))
        legacy = SPINE.replace("Spine Type: root\n", "")
        commit(two, "docs/EPIC-A.md", legacy)
        commit(two, "docs/EPIC-B.md", legacy)
        self.assertIsNone(repo_sync.find_spine(two, self.clock))

    def test_block_root_spine_wins_over_discovery(self) -> None:
        repo = self.repo({"docs/EPIC.md": SPINE, "docs/OTHER-EPIC.md": SPINE.replace("demo", "other"),
                          "AGENTS.md": "<!-- epicspine:begin repo-1 -->\nRoot spine: docs/OTHER-EPIC.md. Read its x\n<!-- epicspine:end -->\n"})
        self.assertEqual(repo_sync.find_spine(repo, self.clock), repo / "docs/OTHER-EPIC.md")


class StopPushTest(Base):
    def setUp(self) -> None:
        super().setUp()
        self.bare, self.repo = self.remote_and_clone("proj", {"docs/EPIC.md": SPINE, "AGENTS.md": "Integration policy: main-direct\n"})
        self.home = self.tmp / "home"
        self.now = 1000.0

    def push(self, repo: Path | None = None) -> str | None:
        self.now += 100  # past the throttle unless a test says otherwise
        return stop_push.push(repo or self.repo, self.clock, self.home, now=self.now)

    def remote_head(self) -> str:
        return git(self.bare, "rev-parse", "main")

    def test_pushes_committed_work_on_the_integration_branch(self) -> None:
        commit(self.repo, "a.txt", "a")
        self.assertEqual(self.push(), "pushed")
        self.assertEqual(self.remote_head(), git(self.repo, "rev-parse", "HEAD"))
        self.assertIsNone(self.push())  # nothing left to push

    def test_untracked_files_do_not_block_but_tracked_edits_do(self) -> None:
        commit(self.repo, "a.txt", "a")
        (self.repo / "scratch.txt").write_text("u")
        (self.repo / "AGENTS.md").write_text("dirty\n")
        self.assertIsNone(self.push())  # mid-edit: the agent has not finished
        self.assertNotEqual(self.remote_head(), git(self.repo, "rev-parse", "HEAD"))
        git(self.repo, "checkout", "-q", "AGENTS.md")
        self.assertEqual(self.push(), "pushed")

    def test_never_commits_dirty_files(self) -> None:
        (self.repo / "AGENTS.md").write_text("dirty\n")
        before = git(self.repo, "rev-parse", "HEAD")
        self.push()
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), before)
        self.assertIn("AGENTS.md", git(self.repo, "status", "--porcelain"))

    def test_pr_approval_opt_out_and_feature_branches_never_push(self) -> None:
        commit(self.repo, "AGENTS.md", "Integration policy: pr-approval\n")
        self.assertIsNone(self.push())
        commit(self.repo, "AGENTS.md", "Integration policy: main-direct\nEpicSpine: off\n")
        self.assertIsNone(self.push())
        commit(self.repo, "AGENTS.md", "Integration policy: main-direct\n")
        (self.repo / ".epicspine-off").write_text("")
        self.assertIsNone(self.push())
        (self.repo / ".epicspine-off").unlink()
        git(self.repo, "checkout", "-q", "-b", "wt/task")
        commit(self.repo, "w.txt", "w")
        self.assertIsNone(self.push())
        self.assertEqual(git(self.bare, "for-each-ref", "--format=%(refname:short)", "refs/heads").split(), ["main"])

    def test_diverged_is_silent_and_never_forced(self) -> None:
        other = self.second_clone(self.bare, "dev")
        commit(other, "d.txt", "d")
        git(other, "push", "-q", "origin", "main")
        commit(self.repo, "a.txt", "a")
        git(self.repo, "fetch", "-q", "origin")  # the local ref now knows it is behind
        self.assertIsNone(self.push())
        self.assertEqual(self.remote_head(), git(other, "rev-parse", "HEAD"))
        # stale ref (no fetch): the server rejects the non-fast-forward; still never forced
        git(self.repo, "update-ref", "refs/remotes/origin/main", git(self.repo, "rev-parse", "HEAD~1"))
        self.assertEqual(self.push(), "failed")
        self.assertEqual(self.remote_head(), git(other, "rev-parse", "HEAD"))

    def test_same_head_is_not_retried_within_a_minute(self) -> None:
        commit(self.repo, "a.txt", "a")
        hook = self.bare / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        self.assertEqual(stop_push.push(self.repo, self.clock, self.home, now=5000.0), "failed")
        self.assertIsNone(stop_push.push(self.repo, self.clock, self.home, now=5030.0))
        self.assertEqual(stop_push.push(self.repo, self.clock, self.home, now=5070.0), "failed")  # a minute later
        commit(self.repo, "b.txt", "b")
        self.assertEqual(stop_push.push(self.repo, self.clock, self.home, now=5071.0), "failed")  # new HEAD: tries at once

    def test_busy_repo_and_no_origin_are_left_alone(self) -> None:
        commit(self.repo, "a.txt", "a")
        (self.repo / ".git" / "MERGE_HEAD").write_text(git(self.repo, "rev-parse", "HEAD") + "\n")
        self.assertIsNone(self.push())
        lone = self.tmp / "lone"
        git(self.tmp, "init", "-q", "-b", "main", str(lone))
        commit(lone, "x", "x")
        self.assertIsNone(self.push(lone))
        self.assertIsNone(self.push(self.tmp))  # not a repo at all

    def run_hook(self, payload: dict, **env: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / "stop_push.py")], input=json.dumps(payload), text=True,
                              capture_output=True, timeout=30, env={**os.environ, "HOME": str(self.home), **env})

    def test_hook_process_pushes_silently_and_always_allows_stop(self) -> None:
        commit(self.repo, "a.txt", "a")
        t0 = time.monotonic()
        proc = self.run_hook({"cwd": str(self.repo), "hook_event_name": "Stop"})
        self.assertLess(time.monotonic() - t0, 8)
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))
        self.assertEqual(self.remote_head(), git(self.repo, "rev-parse", "HEAD"))

    def test_hook_process_survives_garbage_and_honors_sync_off(self) -> None:
        commit(self.repo, "a.txt", "a")
        for stdin in ("", "not json", "[]"):
            proc = subprocess.run([sys.executable, "-B", str(SCRIPTS / "stop_push.py")], input=stdin, text=True, capture_output=True,
                                  cwd=self.tmp, timeout=30, env={**os.environ, "HOME": str(self.home)})
            self.assertEqual((proc.returncode, proc.stdout), (0, ""))
        self.assertNotEqual(self.remote_head(), git(self.repo, "rev-parse", "HEAD"))
        self.run_hook({"cwd": str(self.repo)}, EPICSPINE_SYNC="off")
        self.assertNotEqual(self.remote_head(), git(self.repo, "rev-parse", "HEAD"))

    def test_repo_sync_pulls_and_pushes_without_any_spine(self) -> None:
        bare, repo = self.remote_and_clone("plain", {"README.md": "x\n"})
        dev = self.second_clone(bare, "plaindev")
        commit(dev, "d.txt", "d")
        git(dev, "push", "-q", "origin", "main")
        self.assertEqual(repo_sync.sync(repo, self.clock), ["EpicSpine sync: repo plain main fast-forwarded 1 commit(s)"])
        commit(repo, "a.txt", "a")
        self.assertEqual(repo_sync.sync(repo, self.clock), ["EpicSpine sync: repo plain pushed 1 commit(s) to origin/main"])


class RehookTest(Base):
    """After a skill update (or whenever a hook is missing) the SessionStart hook re-runs install-global, as a subprocess."""

    def setUp(self) -> None:
        super().setUp()
        self.home = self.tmp / "home"
        self.cfg = self.tmp / "cfg"
        self.cx = self.tmp / "cx"
        self.skill = ss.SKILL_DIR
        self.env = {"CLAUDE_CONFIG_DIR": str(self.cfg), "CODEX_HOME": str(self.cx)}
        self.settings = self.cfg / "settings.json"
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        patch = mock.patch.dict(os.environ, {"PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}", "HOME": str(self.home)})
        patch.start()
        self.addCleanup(patch.stop)

    def old_install(self, foreign: bool = True) -> None:
        """What 2026.10.16.4 left behind: SessionStart + url_gate, no Stop push."""
        self.cfg.mkdir()
        self.settings.write_text(json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "mine.sh"}]}]}} if foreign else {}))
        self.assertEqual(global_install.set_hook(self.settings, True, ("url_gate.py",)), "set")

    def heal(self, updated: bool = False) -> str | None:
        return rehook.run(self.env, self.home, self.skill, updated)

    def stops(self) -> list[str]:
        return [h["command"] for g in json.loads(self.settings.read_text())["hooks"]["Stop"] for h in g["hooks"]]

    def test_missing_stop_push_is_registered_once_and_foreign_hooks_survive(self) -> None:
        self.old_install()
        self.assertEqual(self.heal(), "hooks re-registered (Stop push added)")
        self.assertEqual(sorted(Path(c.split('"')[1]).name for c in self.stops()), ["stop_push.py", "url_gate.py"])
        self.assertTrue(all(str(self.skill) in c for c in self.stops()))  # real skill dir, no temp or foreign path
        self.assertIn("mine.sh", self.settings.read_text())
        with mock.patch.object(rehook, "launch", side_effect=AssertionError("current hooks need no subprocess")):
            self.assertIsNone(self.heal())

    def test_update_note_joins_the_skill_line_and_current_hooks_stay_silent(self) -> None:
        self.old_install()
        with mock.patch.object(ss, "sync_skill", return_value="skill 2026.10.16.5 -> 2026.10.16.6"):
            notes = ss.run(self.env, home=self.home, cwd=self.tmp, clock=self.clock)
        self.assertEqual(notes, ["EpicSpine sync: skill 2026.10.16.5 -> 2026.10.16.6; dispatch profile synced; hooks re-registered (Stop push added)"])
        before = self.settings.read_bytes()
        self.assertIsNone(self.heal(updated=True))  # re-runs install-global after another update: nothing changed, nothing said
        self.assertEqual(self.settings.read_bytes(), before)

    def test_only_dirs_that_already_carry_epicspine_are_touched(self) -> None:
        self.assertIsNone(self.heal(updated=True))  # config dir absent
        self.assertFalse(self.cfg.exists())
        self.cfg.mkdir()
        self.settings.write_text('{"model": "x"}')
        (self.cfg / "CLAUDE.md").write_text("mine\n")
        self.assertIsNone(self.heal(updated=True))
        self.assertEqual(self.settings.read_text(), '{"model": "x"}')

    def test_a_hook_registered_from_another_checkout_is_never_repointed(self) -> None:
        other = self.tmp / "other" / "scripts"
        other.mkdir(parents=True)
        (other / "agents_block.py").write_text("")
        self.cfg.mkdir()
        self.settings.write_text(json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": f'python3 "{other / "agents_block.py"}" print-hook'}]}]}}))
        before = self.settings.read_bytes()
        self.assertIsNone(self.heal(updated=True))
        self.assertEqual(self.settings.read_bytes(), before)

    def test_failed_or_slow_install_is_silent_and_retried_at_most_every_ten_minutes(self) -> None:
        self.old_install()
        with mock.patch.object(rehook, "launch", return_value=False) as launch:
            self.assertIsNone(self.heal())
            self.assertIsNone(self.heal())
        self.assertEqual(launch.call_count, 1)
        with mock.patch.object(rehook, "launch", side_effect=RuntimeError("boom")), mock.patch.object(ss, "sync_skill", return_value="skill 1 -> 2"):
            self.assertIsNone(self.heal(updated=True))  # an update is never throttled, and never raises
            self.assertEqual(ss.run(self.env, home=self.home, cwd=self.tmp, clock=self.clock), ["EpicSpine sync: skill 1 -> 2; dispatch profile synced"])

    def test_launch_kills_a_hung_process_group_at_the_deadline(self) -> None:
        t0 = time.monotonic()
        self.assertFalse(rehook.launch([sys.executable, "-c", "import time; time.sleep(30)"], dict(os.environ), 0.5))
        self.assertLess(time.monotonic() - t0, 5)
        self.assertTrue(rehook.launch([sys.executable, "-c", ""], dict(os.environ), 5))

    def test_off_switch_skips_it(self) -> None:
        self.old_install()
        with mock.patch.object(rehook, "launch", side_effect=AssertionError("must not run")):
            self.assertEqual(ss.run({**self.env, "EPICSPINE_SYNC": "off"}, home=self.home, cwd=self.tmp, clock=self.clock), [])

    def fake_codex(self, hang: bool = False) -> None:
        """A `codex` whose app-server answers hooks/list from $CODEX_HOME/hooks.json (or never answers)."""
        script = self.bin / "codex"
        script.write_text("#!%s\nimport json, os, sys, time\n%s"
                          "hooks = os.path.join(os.environ['CODEX_HOME'], 'hooks.json')\n"
                          "for line in sys.stdin:\n    if json.loads(line).get('id') == 2:\n"
                          "        out = [{'key': f'{hooks}:{ev}:{i}:0', 'command': g['hooks'][0]['command'], 'sourcePath': hooks, 'currentHash': f'sha256:{ev}{i}'}\n"
                          "               for ev, gs in json.load(open(hooks))['hooks'].items() for i, g in enumerate(gs)]\n"
                          "        print(json.dumps({'id': 2, 'result': {'data': [{'hooks': out}]}}), flush=True)\n"
                          % (sys.executable, "time.sleep(60)\n" if hang else ""))
        script.chmod(0o755)

    def old_codex(self) -> None:
        self.cx.mkdir()
        (self.cx / "AGENTS.md").write_text(global_install.render_pointer(hookless=True))
        global_install.set_hook(self.cx / "hooks.json", True)  # SessionStart only: pre-.5

    def test_codex_gets_hooks_and_trust_from_the_mocked_app_server(self) -> None:
        self.fake_codex()
        self.old_codex()
        self.assertEqual(self.heal(), "hooks re-registered (codex: Stop push added)")
        self.assertIn("stop_push.py", (self.cx / "hooks.json").read_text())
        self.assertEqual((self.cx / "config.toml").read_text().count("trusted_hash"), 2)
        self.assertFalse(self.cfg.exists())
        with mock.patch.object(rehook, "launch", side_effect=AssertionError("current")):
            self.assertIsNone(self.heal())

    def test_codex_that_never_answers_is_skipped_without_hanging(self) -> None:
        self.fake_codex(hang=True)
        self.old_codex()
        t0 = time.monotonic()
        with mock.patch.object(rehook, "CODEX_TRUST_SECONDS", "1"):
            self.assertEqual(self.heal(), "hooks re-registered (codex: Stop push added)")
        self.assertLess(time.monotonic() - t0, 8)
        self.assertFalse((self.cx / "config.toml").exists())  # untrusted: Codex /hooks or the pointer fallback covers it

    def test_without_a_codex_binary_codex_is_left_alone(self) -> None:
        self.old_codex()
        before = (self.cx / "hooks.json").read_bytes()
        with mock.patch("shutil.which", return_value=None):
            self.assertIsNone(self.heal(updated=True))
        self.assertEqual((self.cx / "hooks.json").read_bytes(), before)

    def test_the_real_hook_process_registers_the_stop_push_hook(self) -> None:
        self.old_install()
        proc = subprocess.run([sys.executable, "-B", str(SCRIPTS / "agents_block.py"), "print-hook"], cwd=self.tmp, text=True, capture_output=True,
                              timeout=60, env={**os.environ, **self.env, "HOME": str(self.home)})
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        self.assertIn("hooks re-registered (Stop push added)", json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"])
        self.assertIn("stop_push.py", self.settings.read_text())


class HookIntegrationTest(Base):
    def test_hook_payload_carries_sync_lines_without_network(self) -> None:
        repo = self.tmp / "r"
        git(self.tmp, "init", "-q", "-b", "main", str(repo))
        commit(repo, "docs/EPIC.md", SPINE)
        home = self.tmp / "home"
        home.mkdir()
        env = {"HOME": str(home), "CLAUDE_CONFIG_DIR": str(self.tmp / "cfg")}
        with mock.patch.dict(os.environ, env), mock.patch.object(ss, "sync_skill", return_value="skill 1 -> 2"), \
                mock.patch.object(Path, "cwd", return_value=repo):
            payload = json.loads(global_install.hook_payload(os.environ))
        ctx = payload["hookSpecificOutput"]["additionalContext"]
        lines = ctx.splitlines()
        self.assertIn("EpicSpine sync: skill 1 -> 2; dispatch profile synced", lines)
        self.assertTrue(any(line.startswith("EpicSpine setup: installed AGENTS.md block and Operating Learnings") for line in lines))
        self.assertNotIn("Machine dispatch profile missing", ctx)  # synced before the warning check
        self.assertEqual((home / ".agents" / "epicspine-profile.md").read_text(), ss.CANONICAL_PROFILE.read_text())

    def test_hook_payload_without_env_never_syncs(self) -> None:
        with mock.patch.object(ss, "run", side_effect=AssertionError("must not run")):
            json.loads(global_install.hook_payload())

    def test_hook_survives_a_broken_sync(self) -> None:
        with mock.patch.object(ss, "run", side_effect=RuntimeError("boom")):
            ctx = json.loads(global_install.hook_payload({}))["hookSpecificOutput"]["additionalContext"]
        self.assertIn("EpicSpine", ctx)

    def test_whole_hook_is_fast_when_offline(self) -> None:
        """Real subprocess, unreachable origin: still well inside the budget."""
        repo = self.tmp / "r"
        git(self.tmp, "init", "-q", "-b", "main", str(repo))
        commit(repo, "AGENTS.md", "Skill updates: off\n")  # keeps the skill step off this checkout's real origin
        git(repo, "remote", "add", "origin", "https://127.0.0.1:9/none.git")
        home = self.tmp / "home"
        home.mkdir()
        t0 = time.monotonic()
        proc = subprocess.run([sys.executable, "-B", str(SCRIPTS / "agents_block.py"), "print-hook"], cwd=repo, text=True,
                              capture_output=True, timeout=30, env={**os.environ, "HOME": str(home), "CLAUDE_CONFIG_DIR": str(self.tmp / "cfg")})
        self.assertLess(time.monotonic() - t0, 12)
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        json.loads(proc.stdout)


if __name__ == "__main__":
    unittest.main()
