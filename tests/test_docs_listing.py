"""doctrine.docs lists .md files from git in a git repo (gitignored data dirs are never walked) and from the tree otherwise; same result either way."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_validate_spine import VALIDATOR_PATH

sys.path.insert(0, str(VALIDATOR_PATH.parent))
import doctrine  # noqa: E402

FILES = ["README.md", "docs/EPIC-1.md", "docs/sub/page.md", "zeta.md", "archive/old.md", ".hidden/x.md", "vendored/SKILL.md", "vendored/deep/ref.md", "data/dump.md"]


class DocsListingTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name).resolve() / "repo"
        for name in FILES:
            (self.repo / name).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / name).write_text("# x\n")

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.repo, check=True, capture_output=True)

    def names(self) -> list[str]:
        return [str(p.relative_to(self.repo)) for p in doctrine.docs(self.repo)]

    def test_walk_outside_git_skips_the_skip_list_and_vendored_skills(self) -> None:
        self.assertEqual(["README.md", "zeta.md", "data/dump.md", "docs/EPIC-1.md", "docs/sub/page.md"], self.names())

    def test_git_lists_the_same_and_leaves_out_gitignored_dirs(self) -> None:
        walked = self.names()
        self.git("init", "-q")
        self.assertEqual(walked, self.names())  # untracked, not ignored: same files, same order
        (self.repo / ".gitignore").write_text("data/\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "x")
        self.assertEqual([n for n in walked if n != "data/dump.md"], self.names())

    def test_untracked_spine_is_seen_and_deleted_tracked_file_is_not(self) -> None:
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "x")
        (self.repo / "docs/EPIC-2.md").write_text("# EPIC-2: new\n")  # never added
        (self.repo / "zeta.md").unlink()
        self.assertEqual(["README.md", "data/dump.md", "docs/EPIC-1.md", "docs/EPIC-2.md", "docs/sub/page.md"], self.names())

    def test_symlinked_doc_resolves_like_the_walk(self) -> None:
        (self.repo / "link.md").symlink_to("docs/EPIC-1.md")
        before = self.names()
        self.git("init", "-q")
        self.assertEqual(before, self.names())
        self.assertIn("docs/EPIC-1.md", before)

    def test_git_failure_falls_back_to_the_walk(self) -> None:
        self.git("init", "-q")
        env = os.environ.copy()
        os.environ["PATH"] = ""  # no git on PATH: subprocess raises, the walk answers
        try:
            self.assertEqual(["README.md", "zeta.md", "data/dump.md", "docs/EPIC-1.md", "docs/sub/page.md"], self.names())
        finally:
            os.environ.clear()
            os.environ.update(env)


if __name__ == "__main__":
    unittest.main()
