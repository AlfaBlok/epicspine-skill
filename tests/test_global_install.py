from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts" / "agents_block.py"
SPEC = importlib.util.spec_from_file_location("agents_block_g", SCRIPT)
assert SPEC and SPEC.loader
ab = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ab
SPEC.loader.exec_module(ab)

import codex_hooks  # noqa: E402  (scripts dir is on sys.path once agents_block is loaded)

REAL_LIST_HOOKS = codex_hooks.list_hooks
MARK = "<!-- epicspine:begin"


class GlobalInstallTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-g-")
        self.home = Path(self._tmp.name)
        for d in (".claude", ".claude_acct2/projects", ".codex", ".config/opencode", ".gemini"):
            (self.home / d).mkdir(parents=True)
        patch = mock.patch("codex_hooks.list_hooks", return_value=None)  # never start the real codex app-server
        patch.start()
        self.addCleanup(patch.stop)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_cmd(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ab.main([*args, "--home", str(self.home)])
        return code, out.getvalue()

    def files(self) -> list[Path]:
        h = self.home
        return [h / ".claude/CLAUDE.md", h / ".claude_acct2/CLAUDE.md", h / ".codex/AGENTS.md",
                h / ".config/opencode/AGENTS.md", h / ".gemini/GEMINI.md"]

    def test_every_adapter_written_with_hooks(self) -> None:
        code, out = self.run_cmd("install-global")
        self.assertEqual(code, 0, out)
        for f in self.files():
            self.assertIn(MARK, f.read_text(encoding="utf-8"), f)
        for s in (".claude", ".claude_acct2", ".gemini"):
            data = json.loads((self.home / s / "settings.json").read_text())
            self.assertIn("print-hook", json.dumps(data["hooks"]["SessionStart"]))
        self.assertFalse((self.home / ".codex/settings.json").exists())

    def test_install_syncs_canonical_profile_and_profile_flag_is_a_local_override(self) -> None:
        profile = self.home / ".agents" / "epicspine-profile.md"
        local = self.home / ".agents" / "epicspine-profile.local.md"
        canonical = (ab.SKILL_DIR / "assets" / "epicspine-profile.md").read_text()
        code, out = self.run_cmd("install-global")
        self.assertIn("machine dispatch profile installed from the skill", out)
        self.assertEqual(profile.read_text(), canonical)
        self.assertNotIn("installed from the skill", self.run_cmd("install-global")[1])
        code, out = self.run_cmd("install-global", "--profile", "model: sonnet")
        self.assertIn("Dispatch profile: model: sonnet", out)
        self.assertEqual(local.read_text(), "Dispatch profile: model: sonnet\n")
        self.assertEqual(profile.read_text(), canonical)
        self.assertNotIn("missing", self.run_cmd("check-global")[1])

    def test_pasted_file_is_pointer_to_live_block(self) -> None:
        self.run_cmd("install-global")
        live = SCRIPT.parent.parent / "assets" / "global-block.md"
        for f in self.files():
            text = f.read_text(encoding="utf-8")
            self.assertIn(f"`{live.resolve()}`", text, f)
            self.assertLessEqual(len(text.splitlines()), 4, f)
            self.assertNotIn("never implements", text, f)
        self.assertIn("never implements", ab.global_install.render_global())

    def test_undetected_and_unsupported_reported(self) -> None:
        _, out = self.run_cmd("install-global")
        self.assertIn("windsurf: not detected", out)
        self.assertIn("cursor (user level): unsupported:", out)
        self.assertIn("aider: unsupported:", out)
        self.assertFalse((self.home / ".codeium").exists())

    def test_idempotent(self) -> None:
        self.run_cmd("install-global")
        snap = {f: f.read_text() for f in self.files()}
        sett = (self.home / ".claude/settings.json").read_text()
        self.run_cmd("install-global")
        self.assertEqual(snap, {f: f.read_text() for f in self.files()})
        self.assertEqual(sett, (self.home / ".claude/settings.json").read_text())
        self.assertEqual(snap[self.files()[0]].count(MARK), 1)

    def test_only_limits_install_to_the_named_harness(self) -> None:
        code, out = self.run_cmd("install-global", "--only", "codex")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.home / ".codex/hooks.json").is_file())
        self.assertFalse((self.home / ".claude/settings.json").exists())
        self.assertFalse((self.home / ".claude/CLAUDE.md").exists())
        self.assertNotIn("claude-code", out)

    def test_no_hooks_flag(self) -> None:
        self.run_cmd("install-global", "--no-hooks")
        self.assertFalse((self.home / ".claude/settings.json").exists())

    def test_preserves_existing_content_and_settings(self) -> None:
        claude_md = self.home / ".claude/CLAUDE.md"
        claude_md.write_text("# Mine\n\nkeep\n")
        settings = self.home / ".claude/settings.json"
        existing = {"model": "x", "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "echo hi"}]}],
                                            "Stop": [{"hooks": []}]}}
        settings.write_text(json.dumps(existing))
        self.run_cmd("install-global")
        self.assertIn("keep", claude_md.read_text())
        data = json.loads(settings.read_text())
        self.assertEqual(data["model"], "x")
        self.assertIn("Stop", data["hooks"])
        self.assertEqual(len(data["hooks"]["SessionStart"]), 2)
        self.run_cmd("uninstall-global")
        self.assertEqual(claude_md.read_text(), "# Mine\n\nkeep\n")
        self.assertEqual(json.loads(settings.read_text()), existing)

    def stop_commands(self, name: str = ".claude") -> list[str]:
        data = json.loads((self.home / name / "settings.json").read_text())
        return [h["command"] for g in data.get("hooks", {}).get("Stop", []) for h in g["hooks"]]

    def test_stop_hook_installed_for_claude_only(self) -> None:
        self.run_cmd("install-global")
        for name in (".claude", ".claude_acct2"):
            cmds = [c for c in self.stop_commands(name) if "url_gate.py" in c]
            self.assertEqual(len(cmds), 1, name)
            self.assertTrue(cmds[0].startswith("python3 "))
        gem = json.loads((self.home / ".gemini/settings.json").read_text())
        self.assertNotIn("Stop", gem["hooks"])

    def test_stop_hook_idempotent_and_coexists_with_foreign(self) -> None:
        settings = self.home / ".claude/settings.json"
        foreign = {"hooks": {"Stop": [
            {"matcher": "", "hooks": [{"type": "command", "command": "other-tool notify"}]},
            {"hooks": [{"type": "command", "command": "second"}]}]}}
        settings.write_text(json.dumps(foreign))
        self.run_cmd("install-global")
        snap = settings.read_text()
        self.run_cmd("install-global")
        self.assertEqual(snap, settings.read_text())
        cmds = self.stop_commands()
        self.assertEqual(sum("url_gate.py" in c for c in cmds), 1)
        self.assertIn("other-tool notify", cmds)
        self.assertIn("second", cmds)
        self.run_cmd("uninstall-global")
        self.assertEqual(json.loads(settings.read_text()), foreign)

    def test_check_reports_missing_stop_hook(self) -> None:
        self.run_cmd("install-global")
        self.assertEqual(self.run_cmd("check-global")[0], 0)
        settings = self.home / ".claude/settings.json"
        data = json.loads(settings.read_text())
        del data["hooks"]["Stop"]
        settings.write_text(json.dumps(data))
        code, out = self.run_cmd("check-global")
        self.assertEqual(code, 1)
        self.assertIn("hook missing", out)

    def test_no_hooks_skips_stop_hook(self) -> None:
        self.run_cmd("install-global", "--no-hooks")
        self.assertFalse((self.home / ".claude/settings.json").exists())

    def test_uninstall_clean(self) -> None:
        self.run_cmd("install-global")
        code, _ = self.run_cmd("uninstall-global")
        self.assertEqual(code, 0)
        for f in self.files():
            self.assertFalse(f.exists(), f)
        self.assertFalse((self.home / ".claude/settings.json").exists())

    def test_invalid_settings_not_clobbered(self) -> None:
        settings = self.home / ".claude/settings.json"
        settings.write_text("{not json")
        code, out = self.run_cmd("install-global")
        self.assertEqual(code, 1)
        self.assertIn("error", out)
        self.assertEqual(settings.read_text(), "{not json")

    def test_check_global(self) -> None:
        self.assertEqual(self.run_cmd("check-global")[0], 1)
        self.run_cmd("install-global")
        self.assertEqual(self.run_cmd("check-global")[0], 0)
        f = self.files()[2]
        f.write_text(f.read_text().replace("Before your first reply", "tampered"))
        code, out = self.run_cmd("check-global")
        self.assertEqual(code, 1)
        self.assertIn("stale", out)

    def test_explicit_claude_dir_creates(self) -> None:
        target = self.home / "elsewhere"
        code, _ = self.run_cmd("install-global", "--claude-dir", str(target))
        self.assertEqual(code, 0)
        self.assertTrue((target / "CLAUDE.md").is_file())
        self.assertFalse((self.home / ".claude/CLAUDE.md").exists())

    def test_nothing_detected(self) -> None:
        empty = self.home / "empty"
        empty.mkdir()
        self.home = empty
        code, out = self.run_cmd("install-global")
        self.assertEqual(code, 1)
        self.assertIn("nothing done", out)

    def link(self, name: str) -> Path:
        return self.home / name / "skills" / "epic-spine"

    def test_config_dir_alias_multiple_dirs_blocks_hooks_links(self) -> None:
        a, b = self.home / ".claude_seat1", self.home / ".claude_seat2"
        code, out = self.run_cmd("install-global", "--config-dir", str(a), "--config-dir", str(b))
        self.assertEqual(code, 0, out)
        for d in (a, b):
            self.assertIn(MARK, (d / "CLAUDE.md").read_text())
            data = json.loads((d / "settings.json").read_text())
            self.assertIn("print-hook", json.dumps(data["hooks"]["SessionStart"]))
            self.assertIn("Stop", data["hooks"])
            link = d / "skills" / "epic-spine"
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), SCRIPT.parent.parent.resolve())
        self.assertIn("skill link linked", out)

    def test_artifact_host_env_set_idempotent_remove(self) -> None:
        a, b = self.home / ".claude_seat1", self.home / ".claude_seat2"
        dirs = ("--config-dir", str(a), "--config-dir", str(b))
        (a).mkdir()
        (a / "settings.json").write_text(json.dumps({"env": {"FOO": "1"}, "model": "x"}))
        _, out = self.run_cmd("install-global", *dirs, "--artifact-host", "tailscale")
        self.assertIn("artifact host set tailscale", out)
        for d in (a, b):
            self.assertEqual(json.loads((d / "settings.json").read_text())["env"]["EPICSPINE_ARTIFACT_HOST"], "tailscale")
        kept = json.loads((a / "settings.json").read_text())
        self.assertEqual((kept["env"]["FOO"], kept["model"]), ("1", "x"))
        _, out = self.run_cmd("install-global", *dirs, "--artifact-host", "tailscale")
        self.assertIn("artifact host current", out)
        _, out = self.run_cmd("install-global", *dirs)  # flag absent: untouched
        self.assertNotIn("artifact host", out)
        self.assertIn("EPICSPINE_ARTIFACT_HOST", (b / "settings.json").read_text())
        _, out = self.run_cmd("install-global", *dirs, "--artifact-host", "")
        self.assertIn("artifact host removed", out)
        self.assertEqual(json.loads((a / "settings.json").read_text())["env"], {"FOO": "1"})
        self.assertNotIn("env", json.loads((b / "settings.json").read_text()))

    def test_artifact_host_bad_env_not_clobbered(self) -> None:
        d = self.home / ".claude_seat1"
        d.mkdir()
        (d / "settings.json").write_text('{"env": []}')
        code, out = self.run_cmd("install-global", "--config-dir", str(d), "--artifact-host", "tailscale")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads((d / "settings.json").read_text())["env"], [])

    def test_skill_link_idempotent_check_and_uninstall(self) -> None:
        self.run_cmd("install-global")
        self.assertTrue(self.link(".claude").is_symlink())
        _, out = self.run_cmd("install-global")
        self.assertIn("skill link current", out)
        self.assertEqual(self.run_cmd("check-global")[0], 0)
        self.link(".claude").unlink()
        code, out = self.run_cmd("check-global")
        self.assertEqual(code, 1)
        self.assertIn("skill link missing", out)
        self.run_cmd("install-global")
        self.run_cmd("uninstall-global")
        self.assertFalse(self.link(".claude").is_symlink())

    def test_check_accepts_foreign_skill_dir(self) -> None:
        self.run_cmd("install-global")
        link = self.link(".claude")
        link.unlink()
        link.mkdir()
        code, out = self.run_cmd("check-global")
        self.assertEqual(code, 0, out)
        self.assertIn("skill link present (foreign)", out)

    def test_foreign_skill_dir_and_link_left_alone(self) -> None:
        real = self.link(".claude")
        real.mkdir(parents=True)
        (real / "SKILL.md").write_text("mine")
        foreign = self.link(".claude_acct2")
        foreign.parent.mkdir(parents=True)
        foreign.symlink_to(self.home / ".codex", target_is_directory=True)
        _, out = self.run_cmd("install-global")
        self.assertIn("skill link foreign, left alone", out)
        self.run_cmd("uninstall-global")
        self.assertEqual((real / "SKILL.md").read_text(), "mine")
        self.assertTrue(foreign.is_symlink())
        self.assertEqual(foreign.resolve(), (self.home / ".codex").resolve())


class CodexHooksTest(unittest.TestCase):
    """Codex 0.131 runs $CODEX_HOME/hooks.json hooks once trusted; `codex app-server hooks/list` is mocked here."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-cx-")
        self.addCleanup(self._tmp.cleanup)
        self.home = Path(self._tmp.name)
        self.codex = self.home / ".codex"
        self.codex.mkdir()
        self.hooks, self.config = self.codex / "hooks.json", self.codex / "config.toml"
        patch = mock.patch("codex_hooks.list_hooks", side_effect=self.fake_codex)
        self.listed = patch.start()
        self.addCleanup(patch.stop)

    def fake_codex(self, codex_dir: Path, seconds: float = 20.0) -> list[dict]:
        out = []
        for event, groups in json.loads(self.hooks.read_text())["hooks"].items():
            for i, group in enumerate(groups):
                for j, hook in enumerate(group["hooks"]):
                    snake = {"SessionStart": "session_start", "Stop": "stop"}.get(event, event.lower())
                    key = f"{self.hooks}:{snake}:{i}:{j}"
                    out.append({"key": key, "command": hook["command"], "sourcePath": str(self.hooks), "currentHash": "sha256:" + str(abs(hash(key)) % 10**8), "trustStatus": "untrusted"})
        return out

    def run_cmd(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ab.main([*args, "--home", str(self.home)])
        return code, out.getvalue()

    def commands(self) -> dict[str, list[str]]:
        data = json.loads(self.hooks.read_text())["hooks"]
        return {event: [h["command"] for g in groups for h in g["hooks"]] for event, groups in data.items()}

    def test_install_registers_sessionstart_and_push_stop_but_not_the_claude_gate(self) -> None:
        code, out = self.run_cmd("install-global")
        self.assertEqual(code, 0, out)
        cmds = self.commands()
        self.assertEqual(len(cmds["SessionStart"]), 1)
        self.assertIn('agents_block.py" print-hook', cmds["SessionStart"][0])
        self.assertEqual(len(cmds["Stop"]), 1)
        self.assertIn('stop_push.py"', cmds["Stop"][0])
        self.assertNotIn("url_gate", json.dumps(cmds))
        self.assertIn("trusted 2 hook(s)", out)

    def test_trust_block_matches_codexs_own_hashes_and_is_idempotent(self) -> None:
        self.run_cmd("install-global")
        text = self.config.read_text()
        for entry in self.fake_codex(self.codex):
            self.assertIn(f'[hooks.state.{json.dumps(entry["key"])}]\ntrusted_hash = "{entry["currentHash"]}"', text)
        self.assertIn("epicspine:begin hooks-trust", text)
        self.run_cmd("install-global")
        self.assertEqual(self.config.read_text(), text)
        self.assertEqual(self.run_cmd("check-global")[0], 0)
        self.assertIn("trust present", self.run_cmd("check-global")[1])

    def test_foreign_hooks_and_config_survive_and_are_never_trusted(self) -> None:
        self.config.write_text('model = "gpt-5"\n\n[projects."/x"]\ntrust_level = "trusted"\n')
        stale = f'\n[hooks.state.{json.dumps(f"{self.hooks}:session_start:1:0")}]\ntrusted_hash = "sha256:old"\n'
        self.config.write_text(self.config.read_text() + stale)
        self.hooks.write_text(json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "mine"}]}],
                                                    "SessionStart": [{"hooks": [{"type": "command", "command": "other"}]}]}}))
        self.run_cmd("install-global")
        text = self.config.read_text()
        self.assertIn('model = "gpt-5"', text)
        self.assertIn('[projects."/x"]', text)
        self.assertNotIn("sha256:old", text)  # our key was rewritten, not duplicated
        self.assertEqual(text.count(f'{self.hooks}:session_start:1:0'), 1)
        self.assertNotIn("pre_tool_use:0:0", text)  # foreign hooks are not trusted for the user
        self.assertNotIn(f"{self.hooks}:session_start:0:0", text)
        cmds = self.commands()
        self.assertEqual(cmds["PreToolUse"], ["mine"])
        self.assertIn("other", cmds["SessionStart"])

    def test_uninstall_removes_hooks_trust_and_pointer_only(self) -> None:
        self.config.write_text('model = "gpt-5"\n')
        agents = self.codex / "AGENTS.md"
        agents.write_text("# Mine\n")
        self.run_cmd("install-global")
        self.assertIn("print-hook", agents.read_text())
        self.run_cmd("uninstall-global")
        self.assertEqual(self.config.read_text(), 'model = "gpt-5"\n')
        self.assertFalse(self.hooks.exists())
        self.assertEqual(agents.read_text(), "# Mine\n")

    def test_uninstall_deletes_a_config_that_only_held_our_block(self) -> None:
        self.run_cmd("install-global")
        self.assertTrue(self.config.is_file())
        self.run_cmd("uninstall-global")
        self.assertFalse(self.config.exists())

    def test_without_a_codex_binary_hooks_stay_unreviewed_and_pointer_covers_it(self) -> None:
        self.listed.side_effect, self.listed.return_value = None, None
        code, out = self.run_cmd("install-global")
        self.assertEqual(code, 0, out)
        self.assertIn("trust not set", out)
        self.assertFalse(self.config.exists())
        self.assertIn("print-hook", (self.codex / "AGENTS.md").read_text())
        self.assertIn("trust not set", self.run_cmd("check-global")[1])

    def test_no_hooks_flag_leaves_codex_hooks_alone_but_pointer_is_written(self) -> None:
        self.run_cmd("install-global", "--no-hooks")
        self.assertFalse(self.hooks.exists())
        self.assertFalse(self.config.exists())

    def test_only_codex_pointer_carries_the_manual_print_hook_instruction(self) -> None:
        self.assertNotIn("print-hook", global_install_pointer(False))
        self.assertIn("print-hook", global_install_pointer(True))

    @unittest.skipUnless(os.environ.get("EPICSPINE_TEST_CODEX") == "1" and shutil.which("codex"), "set EPICSPINE_TEST_CODEX=1 with codex installed")
    def test_real_codex_app_server_reports_our_hooks_as_trusted(self) -> None:
        self.listed.side_effect = REAL_LIST_HOOKS
        self.run_cmd("install-global")
        listed = [h for h in REAL_LIST_HOOKS(self.codex) or [] if "agents_block.py" in h["command"] or "stop_push.py" in h["command"]]
        self.assertEqual(len(listed), 2)
        self.assertEqual({h["trustStatus"] for h in listed}, {"trusted"})


def global_install_pointer(hookless: bool) -> str:
    return sys.modules["global_install"].render_pointer(hookless)


class FirstMessageTest(unittest.TestCase):
    def asset(self, name: str) -> str:
        return (SCRIPT.parent.parent / "assets" / name).read_text(encoding="utf-8")

    def test_global_block_carries_every_shared_rule(self) -> None:
        text = self.asset("global-block.md")
        for needle in ("whatever the message", "`Delivery manager · EpicSpine · Learnings in force:", "final answer",
                       "What do you want?", "≤4 lines", "http://<host>:<port>/<file>", "never a path or `file://`",
                       "Stop hook", "EPICSPINE_DISPATCHER", "local-only", "never implements", "Integrate:",
                       "revert on red", "Record:", "Issue Ledger", "agents_block.py check --repo .",
                       "agents_block.py install --repo ."):
            self.assertIn(needle, text, needle)

    def test_global_block_supersedes_repo_copies_of_shared_rules(self) -> None:
        text = self.asset("global-block.md")
        for needle in ("only repo values apply", "`Dispatch profile:`", "`Integration policy:`", "`Skill updates:`",
                       "its copies of shared rules (bind, dispatch, integrate, record, links/HTML, dispatcher) "
                       "are superseded by this live block"):
            self.assertIn(needle, text, needle)

    def test_repo_block_has_no_shared_rule_text(self) -> None:
        text = self.asset("agents-block.md")
        for needle in ("Bind first", "Delivery manager", "EPICSPINE_", "file://", "http://", "never implements",
                       "Integrate:", "Record:", "pick", "Stop hook"):
            self.assertNotIn(needle, text, needle)
        self.assertLessEqual(len(text.splitlines()), 8)


class RepoFilesTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-r-")
        self.repo = Path(self._tmp.name)
        (self.repo / "docs").mkdir()
        (self.repo / "docs/s.md").write_text("# s\n")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def names(self) -> list[str]:
        return ["AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursor/rules/epicspine.mdc",
                ".github/copilot-instructions.md"]

    def test_all_harness_files_written(self) -> None:
        ab.install(self.repo, "docs/s.md", mirrors=True)
        for n in self.names():
            self.assertIn(MARK, (self.repo / n).read_text(), n)
        self.assertIn("@AGENTS.md", (self.repo / "CLAUDE.md").read_text())
        self.assertIn("alwaysApply: true", (self.repo / ".cursor/rules/epicspine.mdc").read_text())
        self.assertEqual(ab.check(self.repo), 0)

    def test_install_without_mirrors_writes_only_agents(self) -> None:
        ab.install(self.repo, "docs/s.md")
        self.assertEqual(sorted(p.name for p in self.repo.iterdir()), ["AGENTS.md", "docs"])
        self.assertEqual(ab.check(self.repo), 0)

    def test_migration_creates_no_other_files(self) -> None:
        (self.repo / "AGENTS.md").write_text(
            "<!-- epicspine:begin 2026.10.09 -->\n## EpicSpine — always on\n"
            "Root spine: docs/s.md. Read its Current State.\n1. Bind first.\n<!-- epicspine:end -->\n")
        self.assertEqual(ab.main(["install", "--repo", str(self.repo)]), 0)
        self.assertEqual(sorted(p.name for p in self.repo.iterdir()), ["AGENTS.md", "docs"])
        self.assertEqual(ab.check(self.repo), 0)

    def test_existing_mirrors_updated_missing_ones_not_created(self) -> None:
        (self.repo / "CLAUDE.md").write_text("# Claude notes\n")
        gh = self.repo / ".github/copilot-instructions.md"
        gh.parent.mkdir()
        gh.write_text("old\n<!-- epicspine:begin 1 -->\nstale\n<!-- epicspine:end -->\n")
        ab.install(self.repo, "docs/s.md")
        self.assertIn("@AGENTS.md", (self.repo / "CLAUDE.md").read_text())
        self.assertIn("# Claude notes", (self.repo / "CLAUDE.md").read_text())
        self.assertIn("Root spine: docs/s.md.", gh.read_text())
        self.assertFalse((self.repo / "GEMINI.md").exists())
        self.assertFalse((self.repo / ".cursor").exists())
        self.assertEqual(ab.check(self.repo), 0)

    def test_mirrors_flag_creates_them(self) -> None:
        self.assertEqual(ab.main(["install", "--repo", str(self.repo), "--root-spine", "docs/s.md", "--mirrors"]), 0)
        for n in self.names():
            self.assertTrue((self.repo / n).is_file(), n)

    def test_idempotent_and_preserves(self) -> None:
        (self.repo / "CLAUDE.md").write_text("# Claude notes\n")
        ab.install(self.repo, "docs/s.md", mirrors=True)
        snap = {n: (self.repo / n).read_text() for n in self.names()}
        ab.install(self.repo, "docs/s.md", mirrors=True)
        self.assertEqual(snap, {n: (self.repo / n).read_text() for n in self.names()})
        self.assertIn("# Claude notes", snap["CLAUDE.md"])

    def test_uninstall_restores(self) -> None:
        (self.repo / "CLAUDE.md").write_text("# Claude notes\n")
        ab.install(self.repo, "docs/s.md", mirrors=True)
        ab.uninstall(self.repo)
        self.assertEqual((self.repo / "CLAUDE.md").read_text(), "# Claude notes\n")
        for n in ("AGENTS.md", "GEMINI.md", ".cursor/rules/epicspine.mdc", ".github/copilot-instructions.md"):
            self.assertFalse((self.repo / n).exists(), n)

    def test_check_flags_stale_mirror(self) -> None:
        ab.install(self.repo, "docs/s.md", mirrors=True)
        p = self.repo / ".github/copilot-instructions.md"
        p.write_text(p.read_text().replace("override skill defaults", "tampered"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ab.check(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("copilot-instructions.md", out.getvalue())


class HookHealTest(unittest.TestCase):
    """print-hook refreshes a stale pasted copy in the Claude config dir, silently."""

    OLD = ("<!-- epicspine:begin 2026.10.13.2 -->\n## EpicSpine — always on\n1. Bind first.\n"
           "<!-- epicspine:end -->\n")

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-h-")
        self.addCleanup(self._tmp.cleanup)
        self.cdir = Path(self._tmp.name) / "cfg"
        self.cdir.mkdir()
        self.file = self.cdir / "CLAUDE.md"

    def hook(self, **env: str) -> dict:
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "print-hook"], text=True, capture_output=True, timeout=30,
            env={**os.environ, "HOME": self._tmp.name, "CLAUDE_CONFIG_DIR": str(self.cdir), "EPICSPINE_SYNC": "off", **env})
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        out = json.loads(proc.stdout)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        return out

    def test_old_full_copy_replaced_outside_text_kept(self) -> None:
        self.file.write_text("# Mine\n\n" + self.OLD + "\nafter\n")
        self.hook()
        want = ab.global_install.render_pointer().rstrip("\n")
        self.assertEqual(self.file.read_text(), "# Mine\n\n" + want + "\n\nafter\n")
        self.assertEqual([p.name for p in self.cdir.iterdir()], ["CLAUDE.md"])  # no temp litter

    def test_default_dir_is_home_dot_claude(self) -> None:
        (Path(self._tmp.name) / ".claude").mkdir()
        file = Path(self._tmp.name) / ".claude" / "CLAUDE.md"
        file.write_text(self.OLD)
        subprocess.run([sys.executable, "-B", str(SCRIPT), "print-hook"], capture_output=True, timeout=30,
                       env={**{k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"},
                            "HOME": self._tmp.name, "EPICSPINE_SYNC": "off"})
        self.assertEqual(file.read_text(), ab.global_install.render_pointer())

    def test_current_pointer_untouched(self) -> None:
        self.file.write_text("# Mine\n\n" + ab.global_install.render_pointer())
        os.utime(self.file, (1_000_000, 1_000_000))
        self.hook()
        self.assertEqual(self.file.stat().st_mtime, 1_000_000)

    def test_no_block_untouched(self) -> None:
        self.file.write_text("# Mine only\n")
        os.utime(self.file, (1_000_000, 1_000_000))
        self.hook()
        self.assertEqual((self.file.read_text(), self.file.stat().st_mtime), ("# Mine only\n", 1_000_000))
        self.file.unlink()
        self.hook()
        self.assertFalse(self.file.exists())

    def test_unwritable_or_unreadable_keeps_hook_output(self) -> None:
        self.file.write_text(self.OLD)
        self.file.chmod(0o444)
        self.hook()
        self.file.chmod(0o644)
        self.file.unlink()
        self.file.mkdir()  # CLAUDE.md is a directory: read fails
        self.hook()

    def test_missing_machine_profile_warns_present_does_not(self) -> None:
        warn = ab.global_install.PROFILE_WARNING
        ctx = self.hook()["hookSpecificOutput"]["additionalContext"]
        self.assertTrue(ctx.endswith(warn + "\n"))
        self.assertIn("~/.agents/epicspine-profile.md", warn)
        profile = Path(self._tmp.name) / ".agents" / "epicspine-profile.md"
        profile.parent.mkdir()
        profile.write_text("Dispatch profile: x\n")
        ctx = self.hook()["hookSpecificOutput"]["additionalContext"]
        self.assertNotIn("Machine dispatch profile missing", ctx)
        self.assertEqual(ctx, ab.global_install.render_global())
        profile.unlink()
        profile.with_name("epicspine-profile.local.md").write_text("Dispatch profile: mine\n")
        self.assertNotIn("Machine dispatch profile missing", self.hook()["hookSpecificOutput"]["additionalContext"])

    def test_hook_payload_without_env_never_writes(self) -> None:
        self.file.write_text(self.OLD)
        json.loads(ab.global_install.hook_payload())
        self.assertEqual(self.file.read_text(), self.OLD)


if __name__ == "__main__":
    unittest.main()
