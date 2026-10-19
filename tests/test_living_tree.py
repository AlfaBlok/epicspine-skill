"""Living tree: code assignment, closing, --active, stale goals, the SessionStart line, Current State warning (hermetic)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

import test_epic_log as T
from test_agents_block import agents_block

sys.path.insert(0, str(T.SCRIPTS))
import epic_log  # noqa: E402
import session_sync as ss  # noqa: E402


class LivingCase(T.EpicLogCase):
    def git(self, *args: str, when: str | None = None) -> subprocess.CompletedProcess:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        if when:
            env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True, env=env)

    def init(self) -> None:
        self.git("init", "-q")
        agents_block.install(self.repo, "docs/root.md")

    def commit(self, when: str | None = None) -> subprocess.CompletedProcess:
        self.git("add", "-A")
        return self.git("commit", "-m", "x", when=when)

    def title(self, path: str) -> str:
        return (self.repo / path).read_text().splitlines()[0]


class CodeTests(LivingCase):
    def test_next_code_prefix_and_override(self) -> None:
        self.write("docs/E4-old.md", T.E4)
        self.write("docs/old2.md", "# EPIC 7 older\n\nSpine ID: old2\n")
        self.assertEqual(0, self.new("docs/a.md", title="alpha").returncode)
        self.assertEqual("# EPIC-8: alpha", self.title("docs/a.md"))
        self.assertIn("- [ ] E8-1 ", (self.repo / "docs/a.md").read_text())
        self.new("docs/b.md", title="beta")
        self.assertEqual("# EPIC-9: beta", self.title("docs/b.md"))
        self.assertEqual(0, self.new("docs/c.md", "docs/root.md", "gamma", "--code", "20").returncode)
        self.assertEqual("# EPIC-20: gamma", self.title("docs/c.md"))
        self.new("docs/d.md", title="delta")
        self.assertEqual("# EPIC-21: delta", self.title("docs/d.md"))

    def test_first_code_is_never_zero(self) -> None:
        self.new("docs/a.md", title="alpha")
        self.assertEqual("# EPIC-1: alpha", self.title("docs/a.md"))
        self.assertEqual(3, epic_log.next_code(["EPIC-2: x", "E1 y", "EPIC 0 root"]))
        self.assertEqual(1, epic_log.next_code(["EPIC-0: root"]))

    def test_integration_policy_copied(self) -> None:
        self.write("docs/root.md", self.root_text.replace("Integration branch: main\n", "Integration branch: main\nIntegration policy: main-direct\n"))
        self.assertEqual(0, self.new("docs/a.md", title="alpha").returncode)
        self.assertIn("Integration policy: main-direct\n", (self.repo / "docs/a.md").read_text())
        self.assertTrue(T.v.trackable(self.repo / "docs/a.md")["trackable"])


class ClosingTests(LivingCase):
    def setUp(self) -> None:
        super().setUp()
        self.init()
        self.new("docs/a.md", title="alpha")
        self.new("docs/b.md", title="beta")
        self.assertEqual(0, self.commit().returncode)

    def supersede(self, target: str) -> subprocess.CompletedProcess:
        a = self.repo / "docs/a.md"
        a.write_text(a.read_text().replace("Status: draft", "Status: done").replace("Integration branch: main\n", f"Integration branch: main\nSuperseded by: {target}\n"))
        return self.commit()

    def test_superseded_goal_closes_and_is_reported(self) -> None:
        done = self.supersede("[beta](b.md)")
        self.assertEqual(0, done.returncode, done.stderr)
        by = {n["path"]: n for n in self.log()["nodes"]}
        self.assertEqual(("done", "docs/b.md"), (by["docs/a.md"]["status"], by["docs/a.md"]["superseded_by"]))
        self.assertIsNone(by["docs/b.md"]["superseded_by"])

    def test_bad_link_is_blocked(self) -> None:
        for target in ("[x](missing.md)", "[root](../AGENTS.md)"):
            blocked = self.supersede(target)
            self.assertNotEqual(0, blocked.returncode, target)
            self.assertIn("Superseded by", blocked.stderr)
            self.git("reset", "-q", "--hard")


class StaleTests(LivingCase):
    def setUp(self) -> None:
        super().setUp()
        self.init()
        self.new("docs/a.md", title="alpha")
        self.new("docs/b.md", title="beta")
        for n, st in (("a", "active"), ("b", "ready")):
            p = self.repo / f"docs/{n}.md"
            p.write_text(p.read_text().replace("Status: draft", f"Status: {st}"))
        old = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - 30 * 86400))
        self.assertEqual(0, self.commit(when=old).returncode)  # root and both goals are 30 days old
        self.write("docs/root.md", self.root_text + "\nfresh\n")
        self.assertEqual(0, self.commit().returncode)

    def test_json_stale_and_active_list(self) -> None:
        log = self.log()
        self.assertEqual([{"path": "docs/a.md", "title": "EPIC-1: alpha", "days": 30}], log["stale"])  # root fresh, b only ready
        lines = self.run_script("spines.py", "--active").stdout.splitlines()
        self.assertEqual(["Root — active — docs/root.md", "EPIC-1: alpha — active — docs/a.md — STALE 30d", "EPIC-2: beta — ready — docs/b.md"], lines)

    def test_session_line_only_with_stale_goals_and_a_root(self) -> None:
        line = "EpicSpine attention: " + self.repo.name + ": 1 goals active but untouched 14+ days (spines.py --active)"
        self.assertEqual(line, epic_log.attention(self.repo))
        patches = [mock.patch.object(ss, n, return_value=None) for n in ("sync_skill", "sync_profile")]
        with patches[0], patches[1], mock.patch("repo_sync.run", return_value=[]), mock.patch("repo_state.session_lines", return_value=[]), \
                mock.patch("background_sync.attention_lines", return_value=[]):
            self.assertEqual([line], ss.run({}, home=self.repo / "home", cwd=self.repo, clock=ss.Clock(30)))
        (self.repo / "AGENTS.md").write_text("Root spine: none\n")
        self.assertEqual("", epic_log.attention(self.repo))


class CurrentStateWarningTests(LivingCase):
    def test_long_current_state_warns_without_blocking(self) -> None:
        self.init()
        self.new("docs/a.md", title="alpha")
        self.assertEqual(0, self.commit().returncode)
        a = self.repo / "docs/a.md"
        a.write_text(a.read_text().replace("Verified at:", "".join(f"History {i}: x\n" for i in range(5)) + "Verified at:"))
        done = self.commit()
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("keep Current State lean: history goes to Decisions/git", done.stderr)
        a.write_text(a.read_text().replace("".join(f"History {i}: x\n" for i in range(5)), ""))
        self.assertNotIn("keep Current State lean", self.commit().stderr)


if __name__ == "__main__":
    unittest.main()
