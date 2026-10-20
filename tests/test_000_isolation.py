"""Test isolation (EPIC-4 step 9): tests never reach a real harness config dir; the installer refuses to write
outside HOME, to point at a git worktree, or to delete a settings.json."""
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

sys.path.insert(0, str(Path(__file__).parent))
import isolation  # first: redirects the env before any other test module loads
from _safe_env import safe_env

SCRIPTS = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import agents_block as ab  # noqa: E402
import global_install as gi  # noqa: E402
import rehook  # noqa: E402

GIT_ENV = {"GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@example.com"}


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, env={**os.environ, **GIT_ENV})


class IsolationTest(unittest.TestCase):
    def test_config_dirs_are_redirected_to_temp_and_home_is_throwaway(self) -> None:
        home = os.path.realpath(os.environ["HOME"])
        for key in isolation.NAMES:
            self.assertNotEqual(os.environ[key], isolation.ORIGINAL[key])
            self.assertTrue(os.path.realpath(os.environ[key]).startswith(home + os.sep), key)
        self.assertIn("epicspine-test-home-", home)
        self.assertFalse([k for k in os.environ if k.startswith(("GEMINI_", "EPICSPINE_")) and not k.startswith("EPICSPINE_TEST_")])

    def test_safe_env_never_carries_a_real_config_dir(self) -> None:
        leaked = {"CLAUDE_CONFIG_DIR": "/home/someone/.claude_seat1", "CODEX_HOME": "/home/someone/.codex",
                  "XDG_CONFIG_HOME": "/x", "GEMINI_API_KEY": "k", "EPICSPINE_TEST_CODEX": "1"}
        with mock.patch.dict(os.environ, leaked):
            env = safe_env(HOME="/t")
        self.assertEqual((env["HOME"], env["EPICSPINE_TEST_CODEX"]), ("/t", "1"))
        for key in ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "XDG_CONFIG_HOME", "GEMINI_API_KEY"):
            self.assertNotIn(key, env)
        self.assertEqual(safe_env(CLAUDE_CONFIG_DIR="/c")["CLAUDE_CONFIG_DIR"], "/c")


class InstallerGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-iso-")
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(os.path.realpath(self._tmp.name))
        self.home = self.tmp / "home"
        self.home.mkdir()
        patch = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        patch.start()
        self.addCleanup(patch.stop)

    def worktree(self) -> Path:
        """A main checkout holding a copy of the skill dir, plus a linked worktree of it; returns the worktree's skill dir."""
        main = self.tmp / "main"
        skill = main / "skill" / "epic-spine"
        (skill / "assets").mkdir(parents=True)
        (skill / "assets" / "global-block.md").write_text("x\n")
        git(self.tmp, "init", "-q", "-b", "main", str(main))
        git(main, "add", "-A")
        git(main, "commit", "-qm", "seed")
        git(main, "worktree", "add", "-q", "../wt", "-b", "wt/x", "main")
        return self.tmp / "wt" / "skill" / "epic-spine"

    def test_worktree_skill_dir_resolves_to_the_main_checkout(self) -> None:
        wt_skill = self.worktree()
        with mock.patch.object(gi, "SKILL_DIR", wt_skill):
            self.assertEqual(gi.install_dir(), self.tmp / "main" / "skill" / "epic-spine")
            pointer = gi.render_pointer(hookless=True)
        self.assertIn(str(self.tmp / "main" / "skill" / "epic-spine" / "assets" / "global-block.md"), pointer)
        self.assertNotIn(str(self.tmp / "wt"), pointer)

    def test_heal_from_a_worktree_writes_the_canonical_pointer(self) -> None:
        wt_skill = self.worktree()
        cfg = self.home / ".claude"
        cfg.mkdir()
        (cfg / "CLAUDE.md").write_text("<!-- epicspine:begin pointer -->\nold\n<!-- epicspine:end -->\n")
        with mock.patch.object(gi, "SKILL_DIR", wt_skill):
            gi.heal({"CLAUDE_CONFIG_DIR": str(cfg)})
            self.assertEqual(gi.set_hook(cfg / "settings.json", True, ("stop_push.py",)), "set")
        text = (cfg / "CLAUDE.md").read_text() + (cfg / "settings.json").read_text()
        self.assertIn(str(self.tmp / "main" / "skill" / "epic-spine"), text)
        self.assertNotIn(str(self.tmp / "wt"), text)

    def test_worktree_without_a_canonical_dir_writes_nothing(self) -> None:
        wt_skill = self.worktree()
        for gone in (self.tmp / "main" / "skill" / "epic-spine" / "assets" / "global-block.md",):
            gone.unlink()
        cfg = self.home / ".claude"
        cfg.mkdir()
        before = "<!-- epicspine:begin pointer -->\nold\n<!-- epicspine:end -->\n"
        (cfg / "CLAUDE.md").write_text(before)
        err = io.StringIO()
        with mock.patch.object(gi, "SKILL_DIR", wt_skill), mock.patch.object(gi, "_WARNED", set()), mock.patch("sys.stderr", err):
            gi.heal({"CLAUDE_CONFIG_DIR": str(cfg)})
            self.assertTrue(gi.set_hook(cfg / "settings.json", True).startswith("skipped"))
        self.assertEqual((cfg / "CLAUDE.md").read_text(), before)
        self.assertFalse((cfg / "settings.json").exists())
        self.assertIn("git worktree", err.getvalue())

    def test_config_dir_outside_home_is_untouched(self) -> None:
        outside = self.tmp / "seat"
        outside.mkdir()
        files = {"CLAUDE.md": "<!-- epicspine:begin pointer -->\nold\n<!-- epicspine:end -->\n",
                 "settings.json": json.dumps({"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": 'python3 "/x/agents_block.py" print-hook'}]}]}})}
        for name, text in files.items():
            (outside / name).write_text(text)
        err = io.StringIO()
        with mock.patch("sys.stderr", err), mock.patch.object(gi, "_WARNED", set()), contextlib.redirect_stdout(io.StringIO()):
            gi.heal({"CLAUDE_CONFIG_DIR": str(outside)})
            for action in ("install", "uninstall"):
                gi.run(action, self.home, {"CLAUDE_CONFIG_DIR": str(outside)}, [str(outside)], only=("claude-code",))
        self.assertEqual({n: (outside / n).read_text() for n in files}, files)
        self.assertFalse((outside / "skills").exists())
        self.assertIn("outside HOME", err.getvalue())

    def test_rehook_skips_a_config_dir_outside_home(self) -> None:
        outside = self.tmp / "seat"
        outside.mkdir()
        (outside / "CLAUDE.md").write_text("<!-- epicspine:begin pointer -->\nold\n<!-- epicspine:end -->\n")
        with mock.patch.object(rehook, "launch", side_effect=AssertionError("must not run")):
            self.assertIsNone(rehook.heal_one("claude-code", outside, outside / "settings.json", outside / "CLAUDE.md",
                                              gi.STOPS["claude-code"], {}, self.home, True, gi.SKILL_DIR))

    def test_settings_json_is_never_deleted(self) -> None:
        cfg = self.home / ".claude"
        cfg.mkdir()
        settings = cfg / "settings.json"
        settings.write_text("{}\n")  # not ours, and empty: still kept through install and uninstall
        self.assertEqual(gi.set_hook(settings, True, ("stop_push.py",)), "set")
        self.assertEqual(gi.set_hook(settings, False, ("stop_push.py",)), "removed")
        self.assertEqual(json.loads(settings.read_text()), {})
        settings.write_text(json.dumps({"env": {"EPICSPINE_ARTIFACT_HOST": "local"}}))
        self.assertEqual(gi.set_env(settings, ""), "removed")
        self.assertEqual(json.loads(settings.read_text()), {})
        self.assertIs(ab.global_install, gi)


if __name__ == "__main__":
    unittest.main()
