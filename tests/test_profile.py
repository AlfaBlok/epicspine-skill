from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts" / "agents_block.py"
SPEC = importlib.util.spec_from_file_location("agents_block_p", SCRIPT)
assert SPEC and SPEC.loader
ab = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ab
SPEC.loader.exec_module(ab)


class ProfileTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-p-")
        self.root = Path(self._tmp.name)
        self.home = self.root / "home"
        self.addCleanup(self._tmp.cleanup)

    def repo(self, name: str, line: str | None = None) -> Path:
        repo = self.root / name
        (repo / "docs").mkdir(parents=True)
        (repo / "docs" / "spine.md").write_text("Spine ID: x\n" + (line + "\n" if line else ""), encoding="utf-8")
        ab.install(repo, "docs/spine.md")
        return repo

    def run_cli(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ab.main(["profile", "--home", str(self.home), *args])
        return code, out.getvalue().strip()

    def test_unset(self) -> None:
        self.assertEqual(self.run_cli("--repo", str(self.repo("a"))), (3, "unset"))

    def test_set_reused_across_repos(self) -> None:
        self.assertEqual(self.run_cli("--set", "native subagent")[0], 0)
        code, out = self.run_cli("--repo", str(self.repo("b")))
        self.assertEqual(code, 0)
        self.assertIn("native subagent (source: machine", out)

    def test_repo_default_falls_through(self) -> None:
        self.run_cli("--set", "mine")
        code, out = self.run_cli("--repo", str(self.repo("c", "Dispatch profile: default")))
        self.assertEqual((code, "mine" in out, "machine" in out), (0, True, True))

    def test_repo_value_overrides(self) -> None:
        self.run_cli("--set", "mine")
        code, out = self.run_cli("--repo", str(self.repo("d", "Dispatch profile: model: x")))
        self.assertEqual(code, 0)
        self.assertIn("model: x (source: repo docs/spine.md)", out)

    def test_set_twice_one_line(self) -> None:
        self.run_cli("--set", "one")
        self.run_cli("--set", "two")
        text = (self.home / ".agents" / "epicspine-profile.md").read_text(encoding="utf-8")
        self.assertEqual(text, "Dispatch profile: two\n")


if __name__ == "__main__":
    unittest.main()
