"""Return to main: auto-merge of Ready additive branches, merged-branch cleanup, soft reports, state line, cap, table. Hermetic."""
from __future__ import annotations

import io
import json
import os
import shutil
import stat
import subprocess
import sys
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
from test_background_sync import Base, bg, commit, git, ss  # noqa: E402
from test_local_mess import iso  # noqa: E402

import auto_return  # noqa: E402
import repo_state  # noqa: E402

POLICY = {"AGENTS.md": "Integration policy: main-direct\n", "README.md": "x\n"}
GH = """#!/bin/sh
state="$(dirname "$0")/state"; mkdir -p "$state"
echo "gh $*" >> "$state/gh-calls"
[ -f "$state/gh-fail" ] && exit 1
while [ $# -gt 0 ]; do [ "$1" = "--head" ] && head="$2"; shift; done
if grep -qx "$head" "$state/gh-open" 2>/dev/null; then echo '[{"number":7}]'; else echo '[]'; fi
"""


class ReturnBase(Base):
    def setUp(self) -> None:
        super().setUp()
        gh = self.bin / "gh"
        gh.write_text(GH)
        gh.chmod(gh.stat().st_mode | stat.S_IEXEC)

    def gh_open(self, *names: str) -> None:
        (self.bin / "state").mkdir(exist_ok=True)
        (self.bin / "state" / "gh-open").write_text("\n".join(names) + "\n")

    def work(self, cwd: Path, files: dict[str, str | None], ready: bool = True, hours: float = 5) -> str:
        when = iso(hours / 24)
        for rel, text in files.items():
            if text is None:
                (cwd / rel).unlink()
            else:
                (cwd / rel).parent.mkdir(parents=True, exist_ok=True)
                (cwd / rel).write_text(text)
        git(cwd, "add", "-A")
        git(cwd, "commit", "-qm", "work" + ("\n\nReady: yes" if ready else ""), env={"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when})
        return git(cwd, "rev-parse", "HEAD")

    def branch(self, clone: Path, name: str, files: dict[str, str | None] | None = None, ready: bool = True, hours: float = 5,
               worktree: str | None = None, push: bool = False) -> Path:
        """Branch ``name`` off main with one commit; in worktree ``~/github/<worktree>`` or committed in place and left."""
        files = files or {f"docs/{name.replace('/', '-')}.md": "new\n"}
        if worktree:
            path = self.root / worktree
            git(clone, "worktree", "add", "-q", "-b", name, str(path), "main")
        else:
            path = clone
            git(clone, "checkout", "-q", "-b", name, "main")
        self.work(path, files, ready, hours)
        if not worktree:
            git(clone, "checkout", "-q", "main")
        if push:
            git(clone, "push", "-q", "origin", name)
        return path

    def heads(self, bare: Path) -> set[str]:
        return {line.strip().lstrip("* ") for line in git(bare, "branch", "--list").splitlines()}

    def local(self, clone: Path) -> set[str]:
        return {line.strip().lstrip("*+ ") for line in git(clone, "branch", "--list").splitlines()}


class AutoMergeTest(ReturnBase):
    def test_a_ready_additive_branch_is_merged_with_history_and_everything_is_removed(self) -> None:
        bare, clone = self.repo("a", POLICY)
        wt = self.branch(clone, "wt/yoga", worktree="a-yoga", push=True)
        tip = git(wt, "rev-parse", "HEAD")
        entry = self.entry(clone)
        self.assertEqual(entry["mess"], [])
        self.assertEqual(entry["auto"][0], "a: merged wt/yoga into main (--no-ff, pushed)")
        parents = git(bare, "log", "-1", "--format=%P", "main").split()
        self.assertEqual(len(parents), 2)  # a real merge commit, never a squash
        self.assertEqual(git(bare, "merge-base", "--is-ancestor", tip, "main") or "", "")  # the branch's own commit travelled
        self.assertEqual(git(bare, "show", "main:docs/wt-yoga.md"), "new")
        self.assertEqual(self.heads(bare), {"main"})
        self.assertEqual(self.local(clone), {"main"})
        self.assertFalse(wt.exists())
        self.assertEqual(git(clone, "rev-parse", "HEAD"), git(bare, "rev-parse", "main"))  # primary fast-forwarded
        self.assertEqual(len(git(clone, "worktree", "list").splitlines()), 1)  # temp merge worktree is gone too
        self.assertEqual(entry["state"]["worktrees"], 0)

    def test_a_branch_that_only_exists_on_origin_is_merged_too(self) -> None:
        bare, clone = self.repo("a", POLICY)
        other = self.other(bare, "o")
        git(other, "checkout", "-q", "-b", "research/q")
        self.work(other, {"notes/q.md": "q\n"})
        git(other, "push", "-q", "origin", "research/q")
        entry = self.entry(clone)
        self.assertIn("a: merged research/q into main (--no-ff, pushed)", entry["auto"])
        self.assertEqual(self.heads(bare), {"main"})
        self.assertEqual(git(bare, "show", "main:notes/q.md"), "q")

    def test_blocked_branches_stay_untouched_and_are_reported_with_the_reason(self) -> None:
        cases = {"feat/edit": ({"code.py": "print(2)\n"}, True, 5, "it changes or deletes existing files (not purely additive)"),
                 "feat/delete": ({"old.txt": None}, True, 5, "it changes or deletes existing files (not purely additive)"),
                 "feat/fresh": (None, True, 0.5, "last commit under 2 h old"),
                 "feat/workflow": ({".github/workflows/x.yml": "on: push\n"}, True, 5, "it changes or deletes existing files (not purely additive)"),
                 "feat/conflict": ({"same.md": "branch\n"}, True, 5, "it does not merge cleanly")}
        for i, (name, (files, ready, hours, reason)) in enumerate(cases.items()):
            with self.subTest(name):
                bare, clone = self.repo(f"r{i}", {**POLICY, "code.py": "print(1)\n", "old.txt": "o\n"})
                self.branch(clone, name, files, ready, hours)
                self.branch(clone, "feat/unready", ready=False)
                if name == "feat/conflict":
                    commit(clone, "same.md", "main\n")
                    git(clone, "push", "-q", "origin", "main")
                main_tip = git(bare, "rev-parse", "main")
                mess = self.entry(clone)["mess"]
                self.assertEqual(git(bare, "rev-parse", "main"), main_tip)
                self.assertEqual(mess, [f"r{i}: 1 branch(es) marked Ready but not auto-merged: {name} ({reason}) — the manager merges them (ff or --no-ff, never squash)"])
                self.assertTrue({name, "feat/unready"} <= self.local(clone))

    def test_renames_are_not_additive(self) -> None:
        bare, clone = self.repo("a", {**POLICY, "a.md": "a long enough file body\nwith lines\n"})
        git(clone, "checkout", "-q", "-b", "feat/mv", "main")
        git(clone, "mv", "a.md", "b.md")
        git(clone, "commit", "-qm", "mv\n\nReady: yes", env={"GIT_COMMITTER_DATE": iso(1)})
        git(clone, "checkout", "-q", "main")
        self.assertIn("feat/mv (it changes or deletes existing files", self.entry(clone)["mess"][0])

    def test_pull_requests_and_gh_problems_block_the_merge(self) -> None:
        bare, clone = self.repo("a", POLICY)
        self.branch(clone, "feat/pr")
        self.gh_open("feat/pr")
        self.assertIn("feat/pr (it has an open PR)", self.entry(clone)["mess"][0])
        (self.bin / "state" / "gh-fail").write_text("")
        self.assertIn("feat/pr (gh could not check for an open PR, so it is not merged)", self.entry(clone)["mess"][0])
        bare_path = self.tmp / "nogh"  # a PATH that has git and sh but no gh at all
        bare_path.mkdir()
        for tool in ("git", "sh"):
            (bare_path / tool).symlink_to(shutil.which(tool))
        with mock.patch.dict(os.environ, {"PATH": str(bare_path)}):
            self.assertIn("feat/pr (gh could not check", self.entry(clone)["mess"][0])
        self.assertNotIn("a: merged", " ".join(self.entry(clone)["auto"]))
        self.assertEqual(git(bare, "rev-parse", "main"), git(clone, "rev-parse", "main"))  # main never moved
        self.assertEqual(len(git(bare, "log", "--merges", "--format=%H", "main").splitlines()), 0)
        calls = (self.bin / "state" / "gh-calls").read_text()
        self.assertIn("pr list --head feat/pr --state open", calls)

    def test_it_only_runs_in_main_direct_repos_and_not_when_opted_out(self) -> None:
        for name, files, env in (("undeclared", {"README.md": "x\n"}, {}), ("pra", {"AGENTS.md": "Integration policy: pr-approval\n"}, {}),
                                 ("optout", {"AGENTS.md": "Integration policy: main-direct\nAuto-merge: off\n"}, {}),
                                 ("envoff", POLICY, {"EPICSPINE_AUTOMERGE": "OFF"})):
            with self.subTest(name), mock.patch.dict(os.environ, env):
                bare, clone = self.repo(name, files)
                self.branch(clone, "feat/x")
                main_tip = git(bare, "rev-parse", "main")
                entry = self.entry(clone)
                self.assertEqual(entry["auto"], [])
                self.assertEqual(git(bare, "rev-parse", "main"), main_tip)
                if name != "pra":  # pr-approval repos are silent about branches (their PR flow is the process)
                    self.assertIn("feat/x (auto-merge is off or the Integration policy is not main-direct)", entry["mess"][0])

    def test_a_dirty_worktree_or_a_process_inside_blocks_it(self) -> None:
        bare, clone = self.repo("a", POLICY)
        wt = self.branch(clone, "wt/busy", worktree="a-busy")
        (wt / "scratch.txt").write_text("wip\n")
        self.assertIn("wt/busy (its worktree has uncommitted changes)", self.entry(clone)["mess"][0])
        (wt / "scratch.txt").unlink()
        with mock.patch.object(auto_return, "cwds", return_value=[str(wt / "sub")]):
            self.assertIn("wt/busy (a process is running inside its worktree)", self.entry(clone)["mess"][0])
        self.assertTrue(wt.is_dir())
        self.assertIn("wt/busy", self.local(clone))

    @unittest.skipUnless(Path("/proc/self/cwd").exists(), "needs /proc")
    def test_a_real_process_in_the_worktree_is_seen(self) -> None:
        bare, clone = self.repo("a", POLICY)
        wt = self.branch(clone, "wt/busy", worktree="a-busy")
        proc = subprocess.Popen(["sleep", "30"], cwd=str(wt))
        self.addCleanup(proc.kill)
        self.assertIn("a process is running inside its worktree", self.entry(clone)["mess"][0])
        proc.kill()
        proc.wait()
        self.assertIn("a: merged wt/busy", self.entry(clone)["auto"][0])

    def test_the_branch_checked_out_in_the_primary_checkout_is_left_alone(self) -> None:
        bare, clone = self.repo("a", POLICY)
        self.branch(clone, "feat/here")
        git(clone, "checkout", "-q", "feat/here")
        self.assertIn("feat/here (it is checked out)", self.entry(clone)["mess"][0])

    def test_a_rejected_push_stops_reports_and_leaves_no_temp_worktree(self) -> None:
        bare, clone = self.repo("a", POLICY)
        self.branch(clone, "feat/x", push=True)
        hook = bare / "hooks" / "pre-receive"
        hook.write_text('#!/bin/sh\nwhile read old new ref; do [ "$ref" = refs/heads/main ] && exit 1; done\nexit 0\n')
        hook.chmod(0o755)
        main_tip = git(bare, "rev-parse", "main")
        mess = self.entry(clone)["mess"]
        self.assertEqual(mess, ["a: auto-merge of feat/x stopped: origin rejected the push to main — nothing was changed; merge it by hand"])
        self.assertEqual((git(bare, "rev-parse", "main"), self.heads(bare)), (main_tip, {"main", "feat/x"}))
        self.assertIn("feat/x", self.local(clone))
        self.assertEqual(len(git(clone, "worktree", "list").splitlines()), 1)

    def test_at_most_three_merges_per_run_and_force_is_never_used(self) -> None:
        bare, clone = self.repo("a", POLICY)
        for i in range(5):
            self.branch(clone, f"feat/n{i}")
        log = self.tmp / "git.log"
        self.shim_git(f'echo "$*" >> {log}')
        first = self.entry(clone)
        self.assertEqual(len([a for a in first["auto"] if "merged feat/" in a]), 3)
        self.assertIn("(no merge slot left this run)", first["mess"][0])
        self.assertEqual(len([a for a in self.entry(clone)["auto"] if "merged feat/" in a]), 2)
        self.assertEqual(self.local(clone), {"main"})
        pushes = [ln for ln in log.read_text().splitlines() if " push " in f" {ln} "]
        self.assertTrue(pushes and not [p for p in pushes if "--force" in p or " -f" in p])

    def test_offline_does_nothing(self) -> None:
        bare, clone = self.repo("a", POLICY)
        self.branch(clone, "feat/x", push=True)
        result = local_guard(clone, online=False)
        self.assertEqual((result["auto"], result["mess"]), ([], []))
        self.assertIn("feat/x", self.heads(bare))


def local_guard(clone: Path, **kw) -> dict:
    import local_mess
    return local_mess.guard(clone, ss.Clock(30), dict(os.environ), time.time(), [], {}, **kw)


class CleanupAndEscalationTest(ReturnBase):
    def test_branches_already_in_main_are_deleted_locally_and_wt_ones_on_origin(self) -> None:
        bare, clone = self.repo("a", POLICY)
        for name in ("feat/old", "wt/old", "keep/wt"):
            git(clone, "branch", name, "main")
        for name in ("feat/old", "wt/old"):
            git(clone, "checkout", "-q", name)
            self.work(clone, {f"{name.replace('/', '-')}.md": "x\n"}, ready=False, hours=100)
            git(clone, "push", "-q", "origin", name)
            git(clone, "checkout", "-q", "main")
            git(clone, "merge", "-q", "--no-ff", "-m", "m", name)
        git(clone, "push", "-q", "origin", "main")
        git(clone, "worktree", "add", "-q", str(self.root / "a-keep"), "keep/wt")
        commit(clone, "later.md", "later\n")  # main moves on, so tip/same is just an ancestor, not the tip
        git(clone, "push", "-q", "origin", "main")
        git(clone, "branch", "tip/same", "main")
        entry = self.entry(clone)
        self.assertEqual(self.local(clone), {"main", "keep/wt", "tip/same"})
        self.assertEqual(self.heads(bare), {"main", "feat/old"})  # wt/old gone from origin, feat/old only reported
        self.assertEqual(sorted(entry["auto"]), sorted(["a: already in main: deleted local branch feat/old", "a: already in main: deleted local branch wt/old",
                                                        "a: already in main: deleted origin branch wt/old"]))
        self.assertEqual(entry["mess"], ["a: 1 branch(es) already in main — safe to delete: feat/old"])

    def test_an_unmerged_branch_with_new_commits_after_a_merge_is_never_deleted(self) -> None:
        bare, clone = self.repo("a", POLICY)
        self.branch(clone, "wt/x", ready=False, hours=100, push=True)
        git(clone, "merge", "-q", "--no-ff", "-m", "m", "wt/x")
        git(clone, "push", "-q", "origin", "main")
        git(clone, "checkout", "-q", "wt/x")
        extra = self.work(clone, {"more.md": "m\n"}, ready=False, hours=100)  # committed after the merge: not in main
        git(clone, "checkout", "-q", "main")
        git(clone, "push", "-q", "origin", "wt/x")
        self.entry(clone)
        self.assertEqual(git(bare, "rev-parse", "wt/x"), extra)
        self.assertIn("wt/x", self.local(clone))

    def test_idle_branches_get_soft_reminders_by_age_and_nothing_else(self) -> None:
        bare, clone = self.repo("a", POLICY)
        for name, hours in (("feat/new", 24), ("feat/three", 80), ("feat/four", 100), ("feat/old", 20 * 24), ("feat/older", 40 * 24)):
            self.branch(clone, name, ready=False, hours=hours)
        wt = self.branch(clone, "wt/active", ready=False, hours=100, worktree="a-active")
        os.utime(wt, (time.time() - 4 * 86400,) * 2)
        os.utime(wt / "docs", (time.time() - 4 * 86400,) * 2)
        entry = self.entry(clone)
        self.assertEqual(entry["mess"][:2], [
            "a: 2 branch(es) not in main idle >= 3d: feat/four, feat/three — finish and mark `Ready: yes`, merge, or remove",
            f"a: 2 branch(es) not in main idle >= 14d: feat/older, feat/old — {auto_return.PARK}"])
        self.assertEqual(len(entry["mess"]), 3)  # + the worktree line for wt/active (idle 4 d); never a duplicate branch line
        self.assertIn("worktree", entry["mess"][2])
        self.assertTrue({"feat/new", "feat/old", "feat/older"} <= self.local(clone) and wt.is_dir())

    def test_a_worktree_idle_for_two_weeks_is_told_to_park(self) -> None:
        _, clone = self.repo("a", POLICY)
        old = self.root / "a-old"
        git(clone, "worktree", "add", "-q", "-b", "wt/old", str(old), "main")
        self.work(old, {"o.md": "o\n"}, ready=False, hours=20 * 24)
        os.utime(old, (time.time() - 20 * 86400,) * 2)
        self.assertEqual(self.entry(clone)["mess"], [f"a: worktree {old} (wt/old) idle 20d, not merged — {auto_return.PARK}"])

    def test_a_branch_or_worktree_under_an_archive_tag_is_never_reported(self) -> None:
        _, clone = self.repo("a", POLICY)
        self.branch(clone, "feat/parked", ready=False, hours=40 * 24, push=True)
        self.branch(clone, "feat/still-idle", ready=False, hours=40 * 24)
        old = self.root / "a-parked"
        git(clone, "worktree", "add", "-q", "-b", "wt/parked", str(old), "main")
        self.work(old, {"p.md": "p\n"}, ready=False, hours=20 * 24)
        os.utime(old, (time.time() - 20 * 86400,) * 2)
        git(clone, "tag", "-a", "-m", "parked", "archive/feat-parked", "feat/parked")
        git(clone, "tag", "-a", "-m", "parked", "archive/wt-parked", "wt/parked")
        mess = self.entry(clone)["mess"]
        self.assertEqual(mess, [f"a: 1 branch(es) not in main idle >= 14d: feat/still-idle — {auto_return.PARK}"])

    def test_pr_approval_repos_get_no_branch_reminders(self) -> None:
        _, clone = self.repo("a", {"AGENTS.md": "Integration policy: pr-approval\n"})
        self.branch(clone, "feat/old", ready=False, hours=30 * 24)
        self.assertEqual(self.entry(clone)["mess"], [])


class StateAndTableTest(ReturnBase):
    def test_state_line_and_cap_for_the_current_repo(self) -> None:
        bare, clone = self.repo("abnb", POLICY)
        clock = ss.Clock(30)
        self.assertEqual(repo_state.session_lines(clone, clock), ["EpicSpine state: abnb main clean, in sync · worktrees 0 · branches not in main 0"])
        for i in range(4):
            self.branch(clone, f"wt/t{i}", ready=False, worktree=f"abnb-t{i}")
        (clone / "README.md").write_text("changed\n")
        commit(clone, "x.md", "x\n")
        (clone / "README.md").write_text("changed again\n")
        lines = repo_state.session_lines(clone, clock)
        self.assertEqual(lines, ["EpicSpine state: abnb main dirty(1), ahead 1 · worktrees 4 · branches not in main 4",
                                 "EpicSpine attention: abnb: 4 open worktrees (cap 3) — finish or merge one before starting another"])
        from_worktree = repo_state.session_lines(self.root / "abnb-t0", clock)
        self.assertEqual(from_worktree, lines)  # same repo, named by its primary checkout
        git(clone, "checkout", "--", "README.md")
        self.branch(clone, "feat/there", ready=False)
        git(clone, "checkout", "-q", "feat/there")
        self.assertTrue(repo_state.session_lines(clone, clock)[0].endswith("· primary checkout on feat/there"))

    def test_behind_and_diverged_wording_and_quiet_cases(self) -> None:
        info = {"integration": "main", "dirty": 0, "ahead": 0, "behind": 3, "worktrees": 1, "unmerged": 2}
        self.assertIn("main clean, behind 3 ·", repo_state.state_line("r", info))
        self.assertIn("ahead 1, behind 3", repo_state.state_line("r", {**info, "ahead": 1}))
        self.assertIn("sync unknown", repo_state.state_line("r", {**info, "ahead": None}))
        self.assertEqual((repo_state.cap_line("r", 3), repo_state.cap_line("r", 4) is None), (None, False))
        _, clone = self.repo("opt", {"AGENTS.md": "EpicSpine: off\n"})
        self.assertEqual(repo_state.session_lines(clone, ss.Clock(30)), [])
        self.assertEqual(repo_state.session_lines(self.tmp, ss.Clock(30)), [])  # not a repo
        self.assertEqual(repo_state.session_lines(clone, ss.Clock(-1)), [])

    def test_session_start_prints_the_state_line(self) -> None:
        _, clone = self.repo("abnb", POLICY)
        with mock.patch.object(ss, "sync_skill", return_value=None):
            notes = ss.run({"EPICSPINE_SYNC": ""}, home=self.home, cwd=clone, skill_dir=self.skill, clock=ss.Clock(30))
        state = [n for n in notes if n.startswith("EpicSpine state: abnb main ")]  # dirty(1): the block SessionStart just installed
        self.assertEqual(state, ["EpicSpine state: abnb main dirty(1), in sync · worktrees 0 · branches not in main 0"])

    def test_status_file_table_for_every_repo(self) -> None:
        _, a = self.repo("alpha", POLICY)
        self.branch(a, "feat/old", ready=False, hours=30 * 24)
        self.branch(a, "wt/w", ready=False, worktree="alpha-w")
        _, b = self.repo("beta", {"AGENTS.md": "Integration policy: pr-approval\n"})
        commit(b, "local.md", "x\n")
        (b / "AGENTS.md").write_text("Integration policy: pr-approval\ndirty\n")
        self.run_bg()
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(repo_state.main(["--home", str(self.home)]), 0)
        rows = [r.split() for r in buf.getvalue().splitlines()]
        self.assertIn("(background sync)", buf.getvalue().splitlines()[0])
        self.assertEqual(rows[1][:6], ["repo", "main", "state", "ahead/behind", "worktrees", "not"])
        by_name = {r[0]: r for r in rows[2:]}
        self.assertEqual(by_name["alpha"][1:5], ["clean", "0/0", "1", "2"])
        self.assertEqual(by_name["beta"][1:5], ["dirty(1)", "1/0", "0", "0"])
        self.assertIn("1: alpha: 1 branch(es)", buf.getvalue())
        empty = io.StringIO()
        with redirect_stdout(empty):
            self.assertEqual(repo_state.main(["--home", str(self.tmp / "nowhere")]), 1)

    def test_cap_attention_is_recorded_in_the_status_file_not_shown_to_other_repos(self) -> None:
        _, clone = self.repo("abnb", POLICY)
        for i in range(4):
            self.branch(clone, f"wt/t{i}", ready=False, worktree=f"abnb-t{i}")
        self.assertEqual([a for a in self.entry(clone)["attention"] if "cap 3" in a],
                         ["abnb: 4 open worktrees (cap 3) — finish or merge one before starting another"])
        lines = bg.attention_lines(self.home, self.tmp)
        self.assertEqual([], lines)  # recorded for `repo_state.py`, never broadcast into a session about another repo

    def test_background_json_carries_state(self) -> None:
        _, clone = self.repo("abnb", POLICY)
        self.run_bg()
        state = json.loads((self.home / bg.STATUS).read_text())["repos"][str(clone.resolve())]["state"]
        self.assertEqual(state, {"integration": "main", "branch": "main", "dirty": 0, "ahead": 0, "behind": 0, "worktrees": 0, "unmerged": 0})


if __name__ == "__main__":
    unittest.main()
