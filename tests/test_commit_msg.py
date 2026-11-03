"""commit_msg.py: every commit names its ticket (agent_team E63-S7). The hook warns, never blocks; merges and the
agent_team console's own writes are exempt; agents_block.install_hook installs it beside the pre-commit gate."""
from __future__ import annotations

import os
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
                  "rows in docs/spines/epic-62-repo-is-the-source.md", "tidy\n\nPart of E63-S7."):
            self.assertTrue(commit_msg.names_ticket(m), m)

    def test_orphans(self) -> None:
        for m in ("Setup counts the sign-ins", "Document Zenod seat setup outcome", "see https://x.test/E62-S2",
                  "Fix it\n\nRun: run_5c3f5010-56cb\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
                  "tweak\n# E62-S2 in a comment line does not count"):
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

    def test_check_flag(self) -> None:
        out = subprocess.run([sys.executable, str(SCRIPTS / "commit_msg.py"), "--check", "tweak"], capture_output=True, text=True).stdout
        self.assertEqual(out.strip(), "orphan")


if __name__ == "__main__":
    unittest.main()
