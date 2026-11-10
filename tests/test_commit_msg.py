"""commit_msg.py: every commit names its ticket (agent_team E63-S7). The hook warns, never blocks; merges and the
agent_team console's own writes are exempt; agents_block.install_hook installs it beside the pre-commit gate."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "skill" / "epic-spine" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import agents_block  # noqa: E402
import commit_msg  # noqa: E402

ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
       "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}


class NamesTicketTest(unittest.TestCase):
    def test_codes_and_paths_name_a_ticket(self) -> None:
        for m in ("E62-S2: review from spine", "M2-41 fix", "EPIC-63 plan", "Answer EPIC-29-A2", "E34: Waiting on nobody",
                  "E50/E45: seats", "Root L-48: plain words", "Secrets: SK-1 add", "E13-S17c: judge",
                  "rows in docs/spines/epic-62-repo-is-the-source.md", "tidy\n\nPart of E63-S7.",
                  # agent_team E63-S16: prefix-letter codes and root spine files with other names
                  "docs/EPIC_SPINE.md: TAX-A8 feedback done round 2 TAX-A13 (af14531)", "TAX-A9 answered", "ABC-S12 fix",
                  "EPIC.md: tidy", "rows in docs/travel/TRAVEL_SPINE.md", "docs/EPIC-0-ROOT.md: state", "see epic-spine.md"):
            self.assertTrue(commit_msg.names_ticket(m), m)

    def test_orphans(self) -> None:
        for m in ("Setup counts the sign-ins", "Document Zenod seat setup outcome", "see https://x.test/E62-S2",
                  "Fix it\n\nRun: run_5c3f5010-56cb\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
                  "tweak\n# E62-S2 in a comment line does not count",
                  "Use GPT-4o for summaries", "Update README.md and notes.md", "Bump UTF-8x handling", "docs/EPIC_SPINE.mdx draft",
                  "Social pack: Benefit column last on posts so positional ledgers keep their Status (2026.11.07.2)"):
            self.assertFalse(commit_msg.names_ticket(m), m)

    def test_exempt(self) -> None:
        for m in ("Merge branch 'wt/x'", 'Revert "thing"', "fixup! thing", "Team skills: remove diagram (Jordi, via console)",
                  "Stamped ready for delivery (Jordi, asking the Team desk)", "Ask moot: credits are back (console)", ""):
            self.assertTrue(commit_msg.names_ticket(m), m)


class HookTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-commit-msg-")
        self.repo = Path(self._tmp.name)
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True, env=ENV)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def commit(self, msg: str) -> subprocess.CompletedProcess:
        (self.repo / "f.txt").write_text(msg + "\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"], check=True, env=ENV)
        return subprocess.run(["git", "-C", str(self.repo), "commit", "-q", "-m", msg], capture_output=True, text=True, env=ENV)

    def install(self) -> None:
        commit_msg.install(self.repo, f'"{SCRIPTS.parent}"')

    def test_install_hook_puts_both_hooks(self) -> None:
        agents_block.install_hook(self.repo)
        self.assertIn(agents_block.HOOK_MARK, (self.repo / ".git/hooks/pre-commit").read_text())
        self.assertIn(commit_msg.MARK, (self.repo / ".git/hooks/commit-msg").read_text())

    def test_orphan_commit_warns_and_goes_through(self) -> None:
        self.install()
        r = self.commit("tweak the thing")
        self.assertEqual(r.returncode, 0)
        self.assertIn("names no ticket", r.stderr)
        r = self.commit("E63-S7: name the row")
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("names no ticket", r.stderr)
        log = subprocess.run(["git", "-C", str(self.repo), "log", "--format=%s"], capture_output=True, text=True, env=ENV).stdout
        self.assertEqual(log.split("\n")[:2], ["E63-S7: name the row", "tweak the thing"])

    def test_foreign_hook_is_kept(self) -> None:
        hook = self.repo / ".git/hooks/commit-msg"
        hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.install()
        self.assertEqual(hook.read_text(), "#!/bin/sh\nexit 0\n")

    def chainer_dir(self, body: str = "") -> Path:
        """A core.hooksPath dir like infra-vps leak-watch's: each hook runs the common-dir hook (E63-S10)."""
        hooks = Path(self._tmp.name + "-hooks")
        hooks.mkdir()
        self.addCleanup(shutil.rmtree, hooks, True)
        for name in ("pre-commit", "commit-msg"):
            (hooks / name).write_text(body or ("#!/bin/sh\n# leak-watch:hook (test)\nhd=\"$(git rev-parse --git-common-dir)/hooks\"\n"
                                               f'[ -x "$hd/{name}" ] && exec "$hd/{name}" "$@"\nexit 0\n'), encoding="utf-8")
            (hooks / name).chmod(0o755)
        subprocess.run(["git", "-C", str(self.repo), "config", "core.hooksPath", str(hooks)], check=True, env=ENV)
        return hooks

    def test_plain_repo_hooks_land_in_git_hooks(self) -> None:
        self.assertEqual(commit_msg.hook_file(self.repo, "commit-msg").resolve(), (self.repo / ".git/hooks/commit-msg").resolve())
        with tempfile.TemporaryDirectory() as bare:
            self.assertIsNone(commit_msg.hook_file(Path(bare), "commit-msg"))

    def test_leak_watch_hooks_path_installs_beside_the_chainer(self) -> None:
        hooks = self.chainer_dir()
        before = (hooks / "commit-msg").read_text()
        agents_block.install_hook(self.repo)
        self.assertEqual((hooks / "commit-msg").read_text(), before)
        self.assertIn(commit_msg.MARK, (self.repo / ".git/hooks/commit-msg").read_text())
        self.assertIn(agents_block.HOOK_MARK, (self.repo / ".git/hooks/pre-commit").read_text())
        r = self.commit("tweak the thing")
        self.assertEqual(r.returncode, 0)
        self.assertIn("names no ticket", r.stderr)
        self.assertNotIn("names no ticket", self.commit("E63-S10 test").stderr)

    def test_foreign_hooks_path_hook_is_kept(self) -> None:
        hooks = self.chainer_dir("#!/bin/sh\nexit 0\n")
        agents_block.install_hook(self.repo)
        self.assertEqual((hooks / "commit-msg").read_text(), "#!/bin/sh\nexit 0\n")
        self.assertEqual((hooks / "pre-commit").read_text(), "#!/bin/sh\nexit 0\n")
        self.assertFalse((self.repo / ".git/hooks/commit-msg").exists())

    def test_worktree_installs_into_the_common_dir(self) -> None:
        self.commit("E63-S10 base")
        wt = Path(self._tmp.name + "-wt")
        subprocess.run(["git", "-C", str(self.repo), "worktree", "add", "-q", "-b", "side", str(wt)], check=True, env=ENV)
        self.addCleanup(shutil.rmtree, wt, True)
        self.chainer_dir()
        agents_block.install_hook(wt)
        self.assertIn(commit_msg.MARK, (self.repo / ".git/hooks/commit-msg").read_text())
        self.assertIn(agents_block.HOOK_MARK, (self.repo / ".git/hooks/pre-commit").read_text())
        self.assertEqual(list((self.repo / ".git/worktrees").glob("*/hooks")), [])

    def test_check_flag(self) -> None:
        out = subprocess.run([sys.executable, str(SCRIPTS / "commit_msg.py"), "--check", "tweak"], capture_output=True, text=True).stdout
        self.assertEqual(out.strip(), "orphan")


if __name__ == "__main__":
    unittest.main()
