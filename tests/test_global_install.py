from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts" / "agents_block.py"
SPEC = importlib.util.spec_from_file_location("agents_block_g", SCRIPT)
assert SPEC and SPEC.loader
ab = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ab
SPEC.loader.exec_module(ab)

MARK = "<!-- epicspine:begin"


class GlobalInstallTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-g-")
        self.home = Path(self._tmp.name)
        for d in (".claude", ".claude_acct2/projects", ".codex", ".config/opencode", ".gemini"):
            (self.home / d).mkdir(parents=True)

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
        f.write_text(f.read_text().replace("never implements", "tampered"))
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


class FirstMessageTest(unittest.TestCase):
    def test_both_blocks_bootstrap_on_first_message(self) -> None:
        for name in ("agents-block.md", "global-block.md"):
            text = (SCRIPT.parent.parent / "assets" / name).read_text(encoding="utf-8")
            self.assertIn("whatever the message", text, name)
            self.assertIn("`Delivery manager · EpicSpine · Learnings in force:", text, name)
            self.assertIn("final answer", text, name)
            self.assertIn("What do you want?", text, name)
            self.assertIn("http://<host>:<port>/<file>", text, name)
            self.assertIn("never a path or `file://`", text, name)
            self.assertIn("Stop hook", text, name)
            self.assertIn("≤4 lines", text, name)

    def test_blocks_name_machine_dispatcher_and_opt_out(self) -> None:
        for name in ("agents-block.md", "global-block.md"):
            text = (SCRIPT.parent.parent / "assets" / name).read_text(encoding="utf-8")
            self.assertIn("EPICSPINE_DISPATCHER", text, name)
            self.assertIn("local-only", text, name)


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
        ab.install(self.repo, "docs/s.md")
        for n in self.names():
            self.assertIn(MARK, (self.repo / n).read_text(), n)
        self.assertIn("@AGENTS.md", (self.repo / "CLAUDE.md").read_text())
        self.assertIn("alwaysApply: true", (self.repo / ".cursor/rules/epicspine.mdc").read_text())
        self.assertEqual(ab.check(self.repo), 0)

    def test_idempotent_and_preserves(self) -> None:
        (self.repo / "CLAUDE.md").write_text("# Claude notes\n")
        ab.install(self.repo, "docs/s.md")
        snap = {n: (self.repo / n).read_text() for n in self.names()}
        ab.install(self.repo, "docs/s.md")
        self.assertEqual(snap, {n: (self.repo / n).read_text() for n in self.names()})
        self.assertIn("# Claude notes", snap["CLAUDE.md"])

    def test_uninstall_restores(self) -> None:
        (self.repo / "CLAUDE.md").write_text("# Claude notes\n")
        ab.install(self.repo, "docs/s.md")
        ab.uninstall(self.repo)
        self.assertEqual((self.repo / "CLAUDE.md").read_text(), "# Claude notes\n")
        for n in ("AGENTS.md", "GEMINI.md", ".cursor/rules/epicspine.mdc", ".github/copilot-instructions.md"):
            self.assertFalse((self.repo / n).exists(), n)

    def test_check_flags_stale_mirror(self) -> None:
        ab.install(self.repo, "docs/s.md")
        p = self.repo / ".github/copilot-instructions.md"
        p.write_text(p.read_text().replace("never implements", "tampered"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ab.check(self.repo)
        self.assertEqual(code, 1)
        self.assertIn("copilot-instructions.md", out.getvalue())


if __name__ == "__main__":
    unittest.main()
