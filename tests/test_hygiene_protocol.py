"""A sweep is safe by construction: the documented tests classify real fixtures.

All work happens in throwaway temp repositories; the real repo is never touched.
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


def git(cwd, *args, check=True):
    result = subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True
    )
    if check and result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result


def is_merged(repo, branch):
    """Documented 'merged' test: all commits reachable from main."""
    return git(repo, "merge-base", "--is-ancestor", branch, "main", check=False).returncode == 0


def is_clean(worktree):
    """Documented 'clean' test: no uncommitted or untracked changes."""
    return git(worktree, "status", "--porcelain").stdout.strip() == ""


class HygieneProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="epicspine-hygiene-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "proj"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Hygiene Test")
        (self.repo / "README.md").write_text("base\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "base")

    def worktree(self, name):
        path = self.tmp / f"wt-{name}"
        git(self.repo, "worktree", "add", "-b", f"wt/{name}", str(path), "main")
        return path

    def test_classification_and_safe_removal(self):
        merged = self.worktree("merged")
        (merged / "done.txt").write_text("done\n")
        git(merged, "add", "done.txt")
        git(merged, "commit", "-m", "merged work")
        git(self.repo, "merge", "--no-edit", "wt/merged")

        dirty = self.worktree("dirty")
        (dirty / "README.md").write_text("uncommitted change\n")

        unmerged = self.worktree("unmerged")
        (unmerged / "later.txt").write_text("later\n")
        git(unmerged, "add", "later.txt")
        git(unmerged, "commit", "-m", "unmerged work")

        # The three sibling worktrees are visible to the documented check.
        listing = git(self.repo, "worktree", "list").stdout
        for path in (merged, dirty, unmerged):
            self.assertIn(str(path), listing)

        # Documented tests classify each fixture as the protocol says.
        self.assertTrue(is_merged(self.repo, "wt/merged"))
        self.assertTrue(is_clean(merged))
        self.assertFalse(is_merged(self.repo, "wt/unmerged"))
        self.assertTrue(is_clean(unmerged))
        self.assertFalse(is_clean(dirty))

        # Merged + clean: remove the worktree first, then delete with -d.
        self.assertEqual(
            git(self.repo, "worktree", "remove", str(merged), check=False).returncode, 0
        )
        self.assertEqual(
            git(self.repo, "branch", "-d", "wt/merged", check=False).returncode, 0
        )

        # Unmerged is kept: -d refuses it, so no -D is ever needed.
        self.assertNotEqual(
            git(self.repo, "branch", "-d", "wt/unmerged", check=False).returncode, 0
        )
        # Dirty worktree removal without force fails: never force.
        self.assertNotEqual(
            git(self.repo, "worktree", "remove", str(dirty), check=False).returncode, 0
        )

    def test_disk_check_covers_sibling_worktrees(self):
        self.worktree("one")
        measured = subprocess.run(
            ["du", "-sk", "wt-one"], cwd=self.tmp, capture_output=True, text=True
        ).stdout.strip()
        self.assertTrue(measured.endswith("wt-one"))


if __name__ == "__main__":
    unittest.main()
