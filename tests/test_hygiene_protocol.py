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


# The documented scoped measurement: this repo's worktrees only, primary skipped.
DOCUMENTED_SIZE_CMD = (
    "git worktree list --porcelain | sed -n 's/^worktree //p' "
    "| tail -n +2 | xargs -I{} du -sk {} 2>/dev/null"
)


def documented_sizes(repo):
    """Run the documented one-liner; returns its stdout (paths + sizes, or empty)."""
    return subprocess.run(
        DOCUMENTED_SIZE_CMD, cwd=repo, shell=True, capture_output=True, text=True
    ).stdout


def common_git_dir(repo):
    """Resolved common git dir; an orphan of this repo shares this repo's."""
    out = git(repo, "rev-parse", "--git-common-dir").stdout.strip()
    path = Path(out)
    return (path if path.is_absolute() else repo / path).resolve()


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

    def test_disk_check_covers_this_repos_worktrees(self):
        mine = self.worktree("one")
        measured = documented_sizes(self.repo)
        self.assertIn(str(mine.resolve()), measured)

    def test_scope_excludes_foreign_repo_worktrees(self):
        mine = self.worktree("mine")

        # A second, unrelated repo with its own worktree in the same parent.
        other = self.tmp / "other"
        other.mkdir()
        git(other, "init", "-b", "main")
        git(other, "config", "user.email", "test@example.com")
        git(other, "config", "user.name", "Other Test")
        (other / "README.md").write_text("other\n")
        git(other, "add", "README.md")
        git(other, "commit", "-m", "base")
        foreign = self.tmp / "wt-foreign"
        git(other, "worktree", "add", "-b", "wt/foreign", str(foreign), "main")

        # Documented size command measures this repo's worktree, never the foreign one.
        measured = documented_sizes(self.repo)
        self.assertIn(str(mine.resolve()), measured)
        self.assertNotIn(str(foreign.resolve()), measured)

        # Orphan rule: only unregistered *and* sharing this repo's common git dir.
        self.assertNotIn(str(foreign.resolve()), git(self.repo, "worktree", "list").stdout)
        self.assertNotEqual(common_git_dir(foreign), common_git_dir(self.repo))

        # A stale worktree of this repo that git no longer lists still resolves to
        # this repo's common dir, so the documented orphan rule does include it.
        orphan = self.worktree("orphan")
        (orphan / "later.txt").write_text("later\n")
        (self.repo / ".git" / "worktrees" / "wt-orphan" / "gitdir").unlink()
        self.assertNotIn(str(orphan.resolve()), git(self.repo, "worktree", "list").stdout)
        self.assertEqual(common_git_dir(orphan), common_git_dir(self.repo))


if __name__ == "__main__":
    unittest.main()
