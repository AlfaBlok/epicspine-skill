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
