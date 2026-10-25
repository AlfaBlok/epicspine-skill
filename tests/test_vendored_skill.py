"""SessionStart check for old vendored copies of the epic-spine skill inside the current repo. Hermetic: temp dirs only."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import repo_sync  # noqa: E402
import session_sync as ss  # noqa: E402
import vendored_skill as vs  # noqa: E402
from test_session_sync import Base, commit, git  # noqa: E402

FRONT = "---\nname: epic-spine\ndescription: x\n---\n\n# EpicSpine\n"


def line(repo: str, rel: str, have: str, installed: str) -> str:
    return (f"EpicSpine attention: {repo}: old copy of the epic-spine skill at {rel} ({have}, installed {installed}); "
            "agents reading it get stale rules — update or remove it")


class VendoredBase(Base):
    def setUp(self) -> None:
        super().setUp()
        self.home = self.tmp / "home"
        self.installed = self.tmp / "installed" / "epic-spine"
        self.installed.mkdir(parents=True)
        (self.installed / "VERSION").write_text("2026.10.16.8\n")
        self.repo = self.tmp / "zenod"
        git(self.tmp, "init", "-q", "-b", "main", str(self.repo))
        commit(self.repo, "README.md", "x\n")

    def vendor(self, rel: str, version: str | None = "2026.10.01", front: str = FRONT) -> None:
        folder = self.repo / rel
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "SKILL.md").write_text(front)
        if version is not None:
            (folder / "VERSION").write_text(version + "\n")

    def check(self, home: Path | None = None) -> list[str]:
        return vs.check(self.repo, self.clock, home or self.home, self.installed)


class VendoredSkillTest(VendoredBase):
    def test_old_copies_are_named_with_path_and_both_versions(self) -> None:
        self.vendor("skills/epic-spine")
        self.vendor("docs/epicspine-public-repo/skill/epic-spine", "2026.10.02.5")
        self.assertEqual(self.check(), [
            line("zenod", "docs/epicspine-public-repo/skill/epic-spine", "2026.10.02.5", "2026.10.16.8"),
            line("zenod", "skills/epic-spine", "2026.10.01", "2026.10.16.8"),
        ])

    def test_a_copy_within_seven_days_of_the_installed_skill_is_tolerated(self) -> None:
        # installed 2026.10.16.8: zenod's pinned 2026.10.16.9-style neighbours and anything up to 7 days back are fine
        for rel, version in (("a/epic-spine", "2026.10.16.1"), ("b/epic-spine", "2026.10.15.2"), ("c/epic-spine", "2026.10.09.9")):
            self.vendor(rel, version)
        self.assertEqual(self.check(), [])
        self.vendor("d/epic-spine", "2026.10.08.9")  # 8 days older: flagged
        self.assertEqual(self.check(home=self.tmp / "h2"), [line("zenod", "d/epic-spine", "2026.10.08.9", "2026.10.16.8")])

    def test_current_newer_foreign_and_broken_copies_are_silent(self) -> None:
        self.vendor("a/epic-spine", "2026.10.16.8")
        self.vendor("b/epic-spine", "2027.01.01")
        self.vendor("c/other-skill", front="---\nname: other\n---\n")
        self.vendor("d/epic-spine", front="# no frontmatter\nname: epic-spine\n")
        self.vendor("e/epic-spine", version=None)  # SKILL.md without VERSION
        self.vendor("f/epic-spine", "not-a-version")
        self.assertEqual(self.check(), [])

    def test_skipped_dirs_depth_limit_nested_repos_and_the_installed_skill(self) -> None:
        for rel in ("node_modules/x/epic-spine", ".git/x/epic-spine", "wt/job/epic-spine", "worktrees/job/epic-spine",
                    "a/b/c/d/e/epic-spine"):  # depth 6
            self.vendor(rel)
        self.vendor("nested/epic-spine")
        (self.repo / "nested" / ".git").mkdir()  # a nested repo / linked worktree owns its own copy
        self.assertEqual(self.check(), [])
        self.vendor("a/b/c/epic-spine")  # depth 4 is still scanned
        self.assertEqual(self.check(home=self.tmp / "h2"), [line("zenod", "a/b/c/epic-spine", "2026.10.01", "2026.10.16.8")])
        # the installed skill living inside the repo (a source checkout) is never reported
        (self.repo / "skill").mkdir()
        (self.repo / "skill" / "epic-spine").symlink_to(self.installed)
        self.assertEqual(self.check(home=self.tmp / "h3"), [line("zenod", "a/b/c/epic-spine", "2026.10.01", "2026.10.16.8")])

    def test_a_copy_predating_the_deploy_gate_rule_is_flagged_whatever_its_age(self) -> None:
        (self.installed / "VERSION").write_text("2026.10.17.1\n")
        self.vendor("a/epic-spine", "2026.10.16.11")  # one day old, but without the Deploy gate rule
        self.vendor("b/epic-spine", "2026.10.16.12")  # has it
        self.assertEqual(self.check(), [line("zenod", "a/epic-spine", "2026.10.16.11", "2026.10.17.1") + "; it predates the Deploy gate "
                                        "rule (2026.10.16.12): main-direct for every repo, PR/CI only for declared Deploy gate paths"])

    def test_throttled_per_repo(self) -> None:
        self.vendor("skills/epic-spine")
        self.assertEqual(len(self.check()), 1)
        self.assertEqual(self.check(), [])  # within ten minutes: silent
        other = self.tmp / "other"
        git(self.tmp, "init", "-q", "-b", "main", str(other))
        (other / "epic-spine").mkdir()
        (other / "epic-spine" / "SKILL.md").write_text(FRONT)
        (other / "epic-spine" / "VERSION").write_text("2026.10.01\n")
        self.assertEqual(vs.check(other, self.clock, self.home, self.installed),
                         [line("other", "epic-spine", "2026.10.01", "2026.10.16.8")])

    def test_expired_clock_finds_nothing_and_never_raises(self) -> None:
        self.vendor("skills/epic-spine")
        self.assertEqual(vs.check(self.repo, ss.Clock(-1), self.home, self.installed), [])

    def test_at_most_three_lines(self) -> None:
        for name in "abcde":
            self.vendor(f"{name}/epic-spine")
        self.assertEqual(len(self.check()), vs.MAX_LINES)


class SessionStartIntegrationTest(VendoredBase):
    def run_start(self, env: dict | None = None, repo: Path | None = None) -> list[str]:
        env = {"CLAUDE_CONFIG_DIR": str(self.tmp / "cfg"), "CODEX_HOME": str(self.tmp / "cx"), **(env or {})}
        with mock.patch.object(ss, "sync_skill", return_value=None):
            return ss.run(env, home=self.home, cwd=repo or self.repo, skill_dir=self.installed, clock=self.clock)

    def test_session_start_prints_the_attention_line(self) -> None:
        self.vendor("skills/epic-spine")
        notes = [n for n in self.run_start() if "old copy" in n]
        self.assertEqual(notes, [line("zenod", "skills/epic-spine", "2026.10.01", "2026.10.16.8")])
        self.assertEqual([n for n in self.run_start() if "old copy" in n], [])  # throttled

    def test_off_switch_and_repo_opt_out_are_silent(self) -> None:
        self.vendor("skills/epic-spine")
        self.assertEqual([n for n in self.run_start({"EPICSPINE_SYNC": "off"}) if "old copy" in n], [])
        (self.repo / ".epicspine-off").write_text("")
        self.assertEqual(repo_sync.run(self.repo, self.clock, self.home, self.installed), [])
        (self.repo / ".epicspine-off").unlink()
        (self.repo / "AGENTS.md").write_text("EpicSpine: off\n")
        self.assertEqual(repo_sync.run(self.repo, self.clock, self.home, self.installed), [])

    def test_a_clean_repo_adds_nothing(self) -> None:
        self.assertEqual([n for n in self.run_start() if "old copy" in n], [])


if __name__ == "__main__":
    unittest.main()
