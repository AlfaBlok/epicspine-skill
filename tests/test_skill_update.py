from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
SCRIPT_PATH = REPO_ROOT / "skill" / "epic-spine" / "scripts" / "skill_update.py"
SHELL_TOOL = REPO_ROOT / "tools" / "epicspine-manifest.sh"
BLANK_DIGEST = "0" * 64

SPEC = importlib.util.spec_from_file_location("skill_update", SCRIPT_PATH)
assert SPEC and SPEC.loader
skill_update = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = skill_update
SPEC.loader.exec_module(skill_update)


def run_git(args: list[str], cwd: Path) -> str:
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    proc = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, env=env, check=True
    )
    return proc.stdout.strip()


class SkillUpdateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-test-")
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # ------------------------------------------------------------------ #
    # helpers
    # ------------------------------------------------------------------ #

    def write_skill(self, root: Path, version: str, marker: str) -> None:
        skill = root / "skill" / "epic-spine"
        (skill / "scripts").mkdir(parents=True, exist_ok=True)
        (skill / "VERSION").write_text(version + "\n", encoding="utf-8")
        (skill / "SKILL.md").write_text(f"# Skill {marker}\n", encoding="utf-8")
        (skill / "scripts" / "skill_update.py").write_text(
            SCRIPT_PATH.read_text(encoding="utf-8"), encoding="utf-8"
        )

    def refresh_manifest(self, root: Path) -> None:
        manifest = skill_update.generate_manifest(root, "skill/epic-spine")
        (root / "MANIFEST.sha256").write_text(manifest, encoding="utf-8")

    def make_source(self, name: str = "src", version: str = "2026.01.01") -> Path:
        root = self.tmp / name
        self.write_skill(root, version, "one")
        (root / "CHANGELOG.md").write_text(
            "# Changelog\n\n## Unreleased — one\n\n- first change\n", encoding="utf-8"
        )
        self.refresh_manifest(root)
        run_git(["init", "-b", "main"], root)
        run_git(["add", "."], root)
        run_git(["commit", "-m", "initial"], root)
        return root

    def bump_source(self, root: Path, version: str, marker: str) -> str:
        self.write_skill(root, version, marker)
        (root / "CHANGELOG.md").write_text(
            f"# Changelog\n\n## Unreleased — {marker}\n\n- {marker} change\n", encoding="utf-8"
        )
        self.refresh_manifest(root)
        run_git(["add", "."], root)
        run_git(["commit", "-m", marker], root)
        return run_git(["rev-parse", "HEAD"], root)

    def install(self, source: Path, *, commit: str, checked: str | None, tree: bool = True, latest: bool = False) -> Path:
        """Create <tmp>/skills/epic-spine plus a pin marking `commit`."""
        skills = self.tmp / "skills"
        skill = skills / "epic-spine"
        shutil.copytree(source / "skill" / "epic-spine", skill)
        lines = [
            f"source: {source}",
            "path: skill/epic-spine",
            f"commit: {commit}",
            f"manifest: {BLANK_DIGEST}",
            "version: 2026.01.01",
        ]
        if checked is not None:
            lines.append(f"checked: {checked}")
        if tree:
            t = run_git(["rev-parse", "HEAD:skill/epic-spine"], source)
            lines.append(f"tree: {t}")
            if latest:
                lines.append(f"latest: {t}")
        (skills / "epic-spine.SOURCE").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return skills

    def script_in(self, skills: Path) -> Path:
        return skills / "epic-spine" / "scripts" / "skill_update.py"

    def run_update(self, script: Path, *args: str, expect_rc: int | None = 0):
        proc = subprocess.run(
            [sys.executable, "-B", str(script), *args],
            capture_output=True,
            text=True,
        )
        if expect_rc is not None:
            self.assertEqual(
                proc.returncode, expect_rc, f"rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}"
            )
        return proc

    # ------------------------------------------------------------------ #
    # manifest equivalence
    # ------------------------------------------------------------------ #

    def test_python_manifest_equals_shell_tool(self) -> None:
        shell = subprocess.run(
            ["bash", str(SHELL_TOOL), "skill/epic-spine"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        python = skill_update.generate_manifest(REPO_ROOT, "skill/epic-spine")
        self.assertEqual(shell.stdout, python)

    # ------------------------------------------------------------------ #
    # status
    # ------------------------------------------------------------------ #

    def test_status_stale(self) -> None:
        source = self.make_source()
        old_commit = run_git(["rev-parse", "HEAD"], source)
        skills = self.install(source, commit=old_commit, checked="2000-01-01")
        new_commit = self.bump_source(source, "2026.02.02", "two")

        proc = self.run_update(
            self.script_in(skills),
            "status",
            "--json",
            "--source",
            str(source),
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "stale")
        self.assertEqual(payload["installed_commit"], old_commit)
        self.assertEqual(payload["latest_commit"], new_commit)
        self.assertTrue(payload["upgradeable"])
        self.assertFalse(payload["cached"])

    def test_status_fresh(self) -> None:
        source = self.make_source()
        commit = run_git(["rev-parse", "HEAD"], source)
        skills = self.install(source, commit=commit, checked="2000-01-01")

        proc = self.run_update(
            self.script_in(skills), "status", "--json", "--source", str(source)
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "fresh")
        self.assertEqual(payload["installed_commit"], commit)
        self.assertEqual(payload["latest_commit"], commit)

    def test_status_unpinned(self) -> None:
        source = self.make_source()
        skills = self.tmp / "skills"
        shutil.copytree(source / "skill" / "epic-spine", skills / "epic-spine")
        proc = self.run_update(
            self.script_in(skills), "status", "--json", "--source", str(source)
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "unpinned")
        self.assertTrue(payload["upgradeable"])

    def test_cached_answer_does_no_network_call(self) -> None:
        source = self.make_source()
        commit = run_git(["rev-parse", "HEAD"], source)
        today = skill_update.utc_today()
        skills = self.install(source, commit=commit, checked=today, latest=True)

        # A nonexistent source proves no remote call was attempted.
        proc = self.run_update(
            self.script_in(skills),
            "status",
            "--json",
            "--source",
            str(self.tmp / "does-not-exist"),
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "fresh")
        self.assertTrue(payload["cached"])
        self.assertIn("cached", payload["detail"])
        self.assertIsNone(payload["latest_commit"])

    def test_force_bypasses_the_window(self) -> None:
        source = self.make_source()
        old_commit = run_git(["rev-parse", "HEAD"], source)
        skills = self.install(source, commit=old_commit, checked=skill_update.utc_today())
        self.bump_source(source, "2026.02.02", "two")
        proc = self.run_update(
            self.script_in(skills),
            "status",
            "--json",
            "--force",
            "--source",
            str(source),
        )
        self.assertEqual(json.loads(proc.stdout)["status"], "stale")

    def test_unknown_bad_source_modifies_nothing(self) -> None:
        source = self.make_source()
        commit = run_git(["rev-parse", "HEAD"], source)
        skills = self.install(source, commit=commit, checked="2000-01-01")
        pin = skills / "epic-spine.SOURCE"
        before = pin.read_bytes()

        proc = self.run_update(
            self.script_in(skills),
            "status",
            "--json",
            "--source",
            str(self.tmp / "missing-source"),
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "unknown")
        self.assertEqual(pin.read_bytes(), before)

    def test_successful_check_updates_checked(self) -> None:
        source = self.make_source()
        commit = run_git(["rev-parse", "HEAD"], source)
        skills = self.install(source, commit=commit, checked="2000-01-01")
        self.run_update(self.script_in(skills), "status", "--source", str(source))
        pin = skill_update.read_pin(skills / "epic-spine.SOURCE")
        self.assertEqual(pin["checked"], skill_update.utc_today())

    def test_vendored_pin_reports_linked(self) -> None:
        source = self.make_source()
        skills = self.tmp / "skills"
        shutil.copytree(source / "skill" / "epic-spine", skills / "epic-spine")
        (skills / "epic-spine.SOURCE").write_text(
            "source: https://github.com/AlfaBlok/epicspine-skill\n"
            "path: skill/epic-spine\n"
            "commit: deadbeef\n"
            "manifest: skills/epic-spine.manifest.sha256\n",
            encoding="utf-8",
        )
        proc = self.run_update(
            self.script_in(skills), "status", "--json", "--source", str(source)
        )
        self.assertEqual(json.loads(proc.stdout)["status"], "linked")

    # ------------------------------------------------------------------ #
    # upgrade
    # ------------------------------------------------------------------ #

    def test_upgrade_swaps_writes_pin_and_keeps_one_backup(self) -> None:
        source = self.make_source()
        old_commit = run_git(["rev-parse", "HEAD"], source)
        skills = self.install(source, commit=old_commit, checked="2000-01-01")

        stale_backup = skills / "epic-spine.bak"
        stale_backup.mkdir()
        (stale_backup / "SKILL.md").write_text("# Skill stale\n", encoding="utf-8")

        new_commit = self.bump_source(source, "2026.02.02", "two")

        proc = self.run_update(
            self.script_in(skills), "upgrade", "--yes", "--source", str(source)
        )
        self.assertIn("2026.01.01 -> 2026.02.02", proc.stdout)

        installed = skills / "epic-spine"
        self.assertEqual(
            (installed / "SKILL.md").read_text(encoding="utf-8"),
            "# Skill two\n",
        )
        self.assertEqual((installed / "VERSION").read_text().strip(), "2026.02.02")

        pin = skill_update.read_pin(skills / "epic-spine.SOURCE")
        self.assertEqual(pin["commit"], new_commit)
        self.assertRegex(pin["manifest"], r"^[0-9a-f]{64}$")
        self.assertEqual(pin["version"], "2026.02.02")
        self.assertEqual(pin["installed"], skill_update.utc_today())
        self.assertEqual(pin["checked"], skill_update.utc_today())

        backups = list(skills.glob("epic-spine.bak*"))
        self.assertEqual(len(backups), 1)
        backup = backups[0]
        self.assertTrue(backup.is_dir())
        self.assertEqual(
            (backup / "SKILL.md").read_text(encoding="utf-8"), "# Skill one\n"
        )

    def pin_of(self, skills: Path) -> dict:
        return skill_update.read_pin(skills / "epic-spine.SOURCE")

    def status(self, skills: Path, source, *extra: str) -> dict:
        proc = self.run_update(
            self.script_in(skills), "status", "--json", "--source", str(source), *extra
        )
        return json.loads(proc.stdout)

    def test_docs_only_commit_stays_fresh_and_refreshes_commit(self) -> None:
        source = self.make_source()
        skills = self.install(source, commit=run_git(["rev-parse", "HEAD"], source), checked="2000-01-01")
        (source / "NOTES.md").write_text("docs\n", encoding="utf-8")
        run_git(["add", "."], source)
        run_git(["commit", "-m", "docs"], source)
        head = run_git(["rev-parse", "HEAD"], source)
        self.assertEqual(self.status(skills, source)["status"], "fresh")
        self.assertEqual(self.pin_of(skills)["commit"], head)

    def test_skill_change_is_stale_and_cached_stale_persists(self) -> None:
        source = self.make_source()
        skills = self.install(source, commit=run_git(["rev-parse", "HEAD"], source), checked="2000-01-01")
        self.bump_source(source, "2026.02.02", "two")
        self.assertEqual(self.status(skills, source)["status"], "stale")
        pin = self.pin_of(skills)
        self.assertEqual(pin["checked"], skill_update.utc_today())
        self.assertNotEqual(pin["latest"], pin["tree"])
        cached = self.status(skills, self.tmp / "nowhere")
        self.assertEqual((cached["status"], cached["cached"], cached["upgradeable"]), ("stale", True, True))

    def test_legacy_pin_equal_commit_writes_tree(self) -> None:
        source = self.make_source()
        commit = run_git(["rev-parse", "HEAD"], source)
        skills = self.install(source, commit=commit, checked="2000-01-01", tree=False)
        self.assertEqual(self.status(skills, source)["status"], "fresh")
        self.assertEqual(self.pin_of(skills)["tree"], run_git(["rev-parse", "HEAD:skill/epic-spine"], source))

    def test_legacy_pin_different_commit_is_stale_without_tree(self) -> None:
        source = self.make_source()
        skills = self.install(source, commit=run_git(["rev-parse", "HEAD"], source), checked="2000-01-01", tree=False)
        (source / "NOTES.md").write_text("docs\n", encoding="utf-8")
        run_git(["add", "."], source)
        run_git(["commit", "-m", "docs"], source)
        self.assertEqual(self.status(skills, source)["status"], "stale")
        self.assertNotIn("tree", self.pin_of(skills))

    def test_symlinked_hub_not_linked_and_upgrades_in_place(self) -> None:
        source = self.make_source()
        old = run_git(["rev-parse", "HEAD"], source)
        skills = self.install(source, commit=old, checked="2000-01-01")
        harness = self.tmp / "harness"
        harness.mkdir()
        (harness / "epic-spine").symlink_to(skills / "epic-spine", target_is_directory=True)
        self.bump_source(source, "2026.02.02", "two")
        self.assertEqual(self.status(harness, source)["status"], "stale")
        self.run_update(self.script_in(harness), "upgrade", "--yes", "--source", str(source))
        self.assertEqual((skills / "epic-spine" / "SKILL.md").read_text(), "# Skill two\n")
        self.assertEqual(self.status(harness, source, "--force")["status"], "fresh")

    def test_dir_inside_git_repo_is_linked(self) -> None:
        source = self.make_source()
        harness = self.tmp / "harness"
        harness.mkdir()
        (harness / "epic-spine").symlink_to(source / "skill" / "epic-spine", target_is_directory=True)
        self.assertEqual(self.status(harness, source)["status"], "linked")
        self.run_update(self.script_in(harness), "upgrade", "--yes", "--source", str(source), expect_rc=1)

    def test_upgrade_short_circuits_when_tree_equal(self) -> None:
        source = self.make_source()
        skills = self.install(source, commit=run_git(["rev-parse", "HEAD"], source), checked="2000-01-01")
        (source / "NOTES.md").write_text("docs\n", encoding="utf-8")
        run_git(["add", "."], source)
        run_git(["commit", "-m", "docs"], source)
        head = run_git(["rev-parse", "HEAD"], source)
        proc = self.run_update(self.script_in(skills), "upgrade", "--yes", "--source", str(source))
        self.assertIn("Already current", proc.stdout)
        self.assertEqual(list(skills.glob("epic-spine.bak*")), [])
        self.assertEqual(self.pin_of(skills)["commit"], head)
        self.assertNotIn("installed", self.pin_of(skills))

    def test_upgrade_writes_tree_and_latest(self) -> None:
        source = self.make_source()
        skills = self.install(source, commit=run_git(["rev-parse", "HEAD"], source), checked="2000-01-01", tree=False)
        self.bump_source(source, "2026.02.02", "two")
        self.run_update(self.script_in(skills), "upgrade", "--yes", "--source", str(source))
        t = run_git(["rev-parse", "HEAD:skill/epic-spine"], source)
        pin = self.pin_of(skills)
        self.assertEqual((pin["tree"], pin["latest"]), (t, t))


    def test_upgrade_rejects_manifest_mismatch(self) -> None:
        source = self.make_source()
        old_commit = run_git(["rev-parse", "HEAD"], source)
        skills = self.install(source, commit=old_commit, checked="2000-01-01")

        self.bump_source(source, "2026.02.02", "two")
        (source / "MANIFEST.sha256").write_text(f"{BLANK_DIGEST}  skill/epic-spine/SKILL.md\n")
        run_git(["add", "."], source)
        run_git(["commit", "-m", "break manifest"], source)

        pin_before = (skills / "epic-spine.SOURCE").read_bytes()
        self.run_update(
            self.script_in(skills),
            "upgrade",
            "--yes",
            "--source",
            str(source),
            expect_rc=1,
        )
        self.assertEqual(
            (skills / "epic-spine" / "SKILL.md").read_text(encoding="utf-8"),
            "# Skill one\n",
        )
        self.assertEqual((skills / "epic-spine.SOURCE").read_bytes(), pin_before)
        self.assertEqual(list(skills.glob("epic-spine.bak*")), [])
        self.assertFalse((skills / "epic-spine.SOURCE.tmp").exists())


if __name__ == "__main__":
    unittest.main()
