"""Local-mess guard: backup-push of local-only branches and the report-only mess lines. Hermetic (temp HOME, local bare origins)."""
from __future__ import annotations

import json
import os
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
from test_background_sync import Base, bg, commit, git, local_servers, ss  # noqa: E402

import local_mess  # noqa: E402

Proc = local_servers.Proc
REAL_SCAN = local_servers.scan  # Base patches the module attribute
DAY = 86400


def iso(days: float) -> str:
    return datetime.fromtimestamp(time.time() - days * DAY, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


class MessBase(Base):
    def worktree(self, clone: Path, name: str, days: float = 0, files: dict[str, str] | None = None) -> Path:
        """A linked worktree ``~/github/<name>`` on ``wt/<name>`` with one commit and an idle age of ``days``."""
        path = self.root / name
        git(clone, "worktree", "add", "-q", "-b", f"wt/{name}", str(path))
        for rel, text in (files or {f"{name}.txt": "x"}).items():
            commit(path, rel, text, when=iso(days))
        old = time.time() - days * DAY
        os.utime(path, (old, old))
        return path

    def merge(self, clone: Path, name: str) -> None:
        git(clone, "merge", "-q", "--ff-only", f"wt/{name}")
        git(clone, "push", "-q", "origin", "main")

    def remote_heads(self, bare: Path) -> set[str]:
        return {line.strip().lstrip("* ") for line in git(bare, "branch", "--list").splitlines()}

    def reject_pushes(self, bare: Path) -> None:
        hook = bare / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)


class BackupPushTest(MessBase):
    def test_a_local_only_branch_is_pushed_with_upstream_and_never_again(self) -> None:
        bare, clone = self.repo("a")
        git(clone, "checkout", "-q", "-b", "feat/x")
        commit(clone, "x", "1")
        git(clone, "checkout", "-q", "main")
        entry = self.entry(clone)
        self.assertEqual((entry["branches_pushed"], entry["attention"]), (1, []))
        self.assertEqual(git(bare, "rev-parse", "feat/x"), git(clone, "rev-parse", "feat/x"))
        self.assertEqual(git(clone, "config", "branch.feat/x.remote"), "origin")
        self.assertEqual(self.entry(clone)["branches_pushed"], 0)

    def test_new_commits_on_an_already_pushed_branch_fast_forward_it(self) -> None:
        bare, clone = self.repo("a")
        git(clone, "checkout", "-q", "-b", "fix/y")
        commit(clone, "y", "1")
        self.entry(clone)
        commit(clone, "y", "2")
        self.assertEqual(self.entry(clone)["branches_pushed"], 1)
        self.assertEqual(git(bare, "rev-parse", "fix/y"), git(clone, "rev-parse", "fix/y"))

    def test_an_existing_upstream_is_kept(self) -> None:
        bare, clone = self.repo("a")
        git(clone, "checkout", "-q", "-b", "chore/z", "--track", "origin/main")
        commit(clone, "z", "1")
        git(clone, "checkout", "-q", "main")
        self.entry(clone)
        self.assertIn("chore/z", self.remote_heads(bare))
        self.assertEqual(git(clone, "config", "branch.chore/z.merge"), "refs/heads/main")

    def test_nothing_to_back_up_means_no_push(self) -> None:
        bare, clone = self.repo("a")
        git(clone, "branch", "same-as-main")  # commits all on origin/main already
        git(clone, "checkout", "-q", "-b", "mirror")
        commit(clone, "m", "1")
        git(clone, "push", "-q", "origin", "mirror")  # already on origin
        git(clone, "checkout", "-q", "main")
        self.assertEqual(self.entry(clone)["branches_pushed"], 0)
        self.assertEqual(self.remote_heads(bare), {"main", "mirror"})

    def test_the_integration_branch_is_left_to_the_normal_sync(self) -> None:
        bare, clone = self.repo("a", {"AGENTS.md": "Integration branch: develop\n"})
        git(clone, "checkout", "-q", "-b", "develop")
        commit(clone, "d", "1")
        git(clone, "checkout", "-q", "main")
        self.assertEqual(self.entry(clone)["branches_pushed"], 0)
        self.assertNotIn("develop", self.remote_heads(bare))

    def test_pr_approval_repos_still_back_up_worker_branches(self) -> None:
        bare, clone = self.repo("a", {"AGENTS.md": "Integration policy: pr-approval\n"})
        git(clone, "checkout", "-q", "-b", "wt/task")
        commit(clone, "t", "1")
        self.assertEqual(self.entry(clone)["branches_pushed"], 1)
        self.assertIn("wt/task", self.remote_heads(bare))

    def test_opt_outs_env_and_repo_line(self) -> None:
        bare, clone = self.repo("a")
        bare2, clone2 = self.repo("b", {"AGENTS.md": "Push branches: off\n"})
        for repo in (clone, clone2):
            git(repo, "checkout", "-q", "-b", "wt/t")
            commit(repo, "t", "1")
        with mock.patch.dict(os.environ, {"EPICSPINE_PUSH_BRANCHES": "OFF"}):
            repos = self.run_bg()
        self.assertEqual([repos[str(c.resolve())]["branches_pushed"] for c in (clone, clone2)], [0, 0])
        self.assertEqual((self.remote_heads(bare), self.remote_heads(bare2)), ({"main"}, {"main"}))
        self.assertEqual(self.entry(clone)["branches_pushed"], 1)  # env off was the only thing stopping repo a
        self.assertEqual(self.remote_heads(bare2), {"main"})  # b keeps its own opt-out

    def test_a_diverged_branch_is_attention_and_origin_is_untouched(self) -> None:
        bare, clone = self.repo("a")
        git(clone, "checkout", "-q", "-b", "feat/x")
        commit(clone, "mine", "1")
        other = self.other(bare, "o")
        git(other, "checkout", "-q", "-b", "feat/x", "origin/main")
        commit(other, "theirs", "1")
        git(other, "push", "-q", "origin", "feat/x")
        theirs = git(bare, "rev-parse", "feat/x")
        entry = self.entry(clone)
        self.assertEqual(entry["branches_pushed"], 0)
        self.assertEqual(len(entry["attention"]), 1)
        self.assertIn("a: branch feat/x has 1 commit(s) only on this machine and origin/feat/x diverged", entry["attention"][0])
        self.assertIn("never force", entry["attention"][0])
        self.assertEqual(git(bare, "rev-parse", "feat/x"), theirs)

    def test_a_rejected_push_is_attention_and_is_not_forced(self) -> None:
        bare, clone = self.repo("a")
        self.reject_pushes(bare)
        git(clone, "checkout", "-q", "-b", "wt/t")
        commit(clone, "t", "1")
        entry = self.entry(clone)
        self.assertEqual(entry["branches_pushed"], 0)
        self.assertEqual(entry["attention"], ["a: branch wt/t has 1 commit(s) only on this machine and the push was rejected — "
                                              "merge or rebase it with origin/wt/t, never force"])
        self.assertEqual(self.remote_heads(bare), {"main"})
        log = self.tmp / "git.log"
        self.shim_git(f'echo "$*" >> {log}')
        self.entry(clone)
        self.assertFalse([line for line in log.read_text().splitlines() if "push" in line and ("--force" in line or " -f" in line)])

    def test_at_most_ten_pushes_per_run_the_rest_next_time(self) -> None:
        bare, clone = self.repo("a")
        for i in range(3):
            git(clone, "checkout", "-q", "-b", f"wt/t{i}", "main")
            commit(clone, f"t{i}", "1")
        git(clone, "checkout", "-q", "main")
        self.assertEqual(local_mess.PUSH_MAX, 10)
        with mock.patch.object(local_mess, "PUSH_MAX", 2):
            self.assertEqual(self.entry(clone)["branches_pushed"], 2)
            self.assertEqual(self.entry(clone)["branches_pushed"], 1)
        self.assertEqual(len(self.remote_heads(bare)), 4)

    def test_a_hung_push_is_cut_off_and_retried_next_run(self) -> None:
        bare, clone = self.repo("a")
        git(clone, "checkout", "-q", "-b", "wt/t")
        commit(clone, "t", "1")
        self.shim_git('case "$*" in *push*) exec sleep 30;; esac')
        t0 = time.monotonic()
        with mock.patch.object(local_mess, "PUSH_SECONDS", 1.0):
            entry = self.entry(clone)
        self.assertLess(time.monotonic() - t0, 12)
        self.assertEqual((entry["branches_pushed"], entry["attention"]), (0, []))
        (self.bin / "git").unlink()
        self.assertEqual(self.entry(clone)["branches_pushed"], 1)

    def test_the_guard_budget_is_bounded_and_an_expired_clock_does_nothing(self) -> None:
        _, clone = self.repo("a")
        git(clone, "checkout", "-q", "-b", "wt/t")
        commit(clone, "t", "1")
        self.assertEqual(local_mess.MESS_SECONDS, 40.0)
        result = local_mess.guard(clone, ss.Clock(0), {}, time.time(), [], {})
        self.assertEqual((result["branches_pushed"], result["attention"], result["mess"]), (0, [], []))

    def test_opted_out_repos_are_not_touched(self) -> None:
        bare, clone = self.repo("a", {"AGENTS.md": "EpicSpine: off\n"})
        git(clone, "checkout", "-q", "-b", "wt/t")
        commit(clone, "t", "1")
        self.assertEqual(self.run_bg(), {})
        self.assertEqual(self.remote_heads(bare), {"main"})


class WorktreeReportTest(MessBase):
    def test_idle_unmerged_worktree_is_reported_with_age_and_nothing_is_changed(self) -> None:
        _, clone = self.repo("abnb")
        old = self.worktree(clone, "wt-old", days=5)
        self.worktree(clone, "wt-fresh", days=1)
        heads = git(old, "rev-parse", "HEAD")
        entry = self.entry(clone)
        self.assertEqual(entry["mess"], [f"abnb: worktree {old} (wt/wt-old) idle 5d, not merged — merge it or remove it"])
        self.assertTrue(old.is_dir())
        self.assertEqual(git(old, "rev-parse", "HEAD"), heads)
        self.assertEqual(git(clone, "branch", "--list", "wt/wt-old").strip(), "+ wt/wt-old")

    def test_recent_dirty_edits_keep_a_worktree_active(self) -> None:
        _, clone = self.repo("abnb")
        old = self.worktree(clone, "wt-busy", days=5)
        (old / "wt-busy.txt").write_text("still editing\n")  # fresh mtime on a changed file
        self.assertEqual(self.entry(clone)["mess"], [])

    def test_merged_clean_worktree_is_safe_to_remove_but_not_while_fresh_or_dirty(self) -> None:
        _, clone = self.repo("abnb")
        trees = []
        for name, days in (("wt-done", 2), ("wt-new", 0), ("wt-dirty", 2)):
            trees.append(self.worktree(clone, name, days=days))
            self.merge(clone, name)
        done, fresh, dirty = trees
        (dirty / "scratch.txt").write_text("x")
        os.utime(dirty / "scratch.txt", (time.time() - 5 * DAY,) * 2)
        os.utime(dirty, (time.time() - 5 * DAY,) * 2)
        self.assertEqual(self.entry(clone)["mess"], [f"abnb: worktree {done} already merged — safe to remove (git worktree remove {done})"])
        self.assertTrue(done.is_dir() and fresh.is_dir() and dirty.is_dir())

    def test_at_most_three_lines_then_a_count(self) -> None:
        _, clone = self.repo("abnb")
        for i in range(5):
            self.worktree(clone, f"wt-{i}", days=6)
        mess = self.entry(clone)["mess"]
        self.assertEqual(len(mess), 4)
        self.assertEqual(mess[-1], "abnb: 2 more worktrees (see git worktree list, ps)")

    def test_a_missing_origin_integration_ref_or_no_worktrees_report_nothing(self) -> None:
        _, clone = self.repo("abnb")
        self.assertEqual(self.entry(clone)["mess"], [])
        old = self.worktree(clone, "wt-old", days=5)
        with mock.patch.object(local_mess, "linked_worktrees", return_value=[(old, "wt/wt-old")]):
            git(clone, "update-ref", "-d", "refs/remotes/origin/main")
            clock = ss.Clock(30)
            self.assertEqual(local_mess.worktree_lines(clone, clock, "main", time.time(), [(old, "wt/wt-old")]), [])


class DirtyReportTest(MessBase):
    def dirty(self, clone: Path, name: str, hours: float) -> None:
        (clone / name).write_text("changed\n")
        os.utime(clone / name, (time.time() - hours * 3600,) * 2)

    def test_old_uncommitted_tracked_changes_are_reported_and_left_alone(self) -> None:
        _, clone = self.repo("infra", {"report.md": "a\n", "other.md": "b\n"})
        self.dirty(clone, "report.md", 30.5)
        (clone / "untracked.txt").write_text("u")
        entry = self.entry(clone)
        self.assertEqual(entry["mess"], ["infra: uncommitted changes for 30h in report.md — commit them or discard"])
        self.assertEqual((clone / "report.md").read_text(), "changed\n")
        self.assertEqual(git(clone, "status", "--porcelain"), "M report.md\n?? untracked.txt")

    def test_fresh_changes_and_untracked_files_are_not_reported(self) -> None:
        _, clone = self.repo("infra", {"report.md": "a\n"})
        self.dirty(clone, "report.md", 2)
        (clone / "new.txt").write_text("u")
        os.utime(clone / "new.txt", (time.time() - 90 * 3600,) * 2)
        entry = self.entry(clone)
        self.assertEqual(entry["mess"], [])
        self.assertIsNotNone(entry["dirty_since"])

    def test_a_cron_rewritten_file_counts_from_when_it_was_first_seen_dirty(self) -> None:
        _, clone = self.repo("infra", {"report.md": "a\n"})
        self.dirty(clone, "report.md", 1)  # rewritten an hour ago, as a daily job does
        self.entry(clone)
        data = json.loads((self.home / bg.STATUS).read_text())
        data["repos"][str(clone.resolve())]["dirty_since"] = time.time() - 40.5 * 3600
        (self.home / bg.STATUS).write_text(json.dumps(data))
        self.assertEqual(self.entry(clone)["mess"], ["infra: uncommitted changes for 40h in report.md — commit them or discard"])
        git(clone, "checkout", "--", "report.md")
        entry = self.entry(clone)
        self.assertEqual((entry["mess"], entry["dirty_since"]), ([], None))

    def test_many_files_are_summarised(self) -> None:
        _, clone = self.repo("infra", {f"f{i}.md": "a\n" for i in range(5)})
        for i in range(5):
            self.dirty(clone, f"f{i}.md", 30.5)
        self.assertEqual(self.entry(clone)["mess"], ["infra: uncommitted changes for 30h in f0.md, f1.md, f2.md +2 more — commit them or discard"])

    def test_linked_worktrees_are_not_treated_as_the_main_checkout(self) -> None:
        _, clone = self.repo("infra", {"a.md": "a\n"})
        wt = self.worktree(clone, "wt-x", days=0)
        (wt / "wt-x.txt").write_text("edited\n")
        os.utime(wt / "wt-x.txt", (time.time() - 30 * 3600,) * 2)
        self.assertEqual(self.entry(clone)["mess"], [])


class ServerReportTest(MessBase):
    def procs(self, wt: Path) -> list[Proc]:
        return [Proc(111, str(wt), ["python3", "-m", "http.server", "8801"], 2.2 * DAY),
                Proc(222, str(self.tmp), ["python3", "-m", "http.server", "8802", "--directory", str(wt / "site")], 3.1 * DAY),
                Proc(333, str(wt), ["python3", "-m", "http.server", "8803"], 3 * 3600),  # young
                Proc(444, str(wt), ["bash"], 9 * DAY),  # a shell, not a server
                Proc(555, str(wt), ["python3", "-m", "http.server", "--directory", str(self.tmp)], 9 * DAY),  # serves elsewhere
                Proc(666, str(self.tmp), ["python3", "-m", "http.server"], 9 * DAY)]  # outside every worktree

    def test_old_servers_inside_a_worktree_are_reported_and_never_killed(self) -> None:
        _, clone = self.repo("abnb")
        wt = self.worktree(clone, "wt-yoga", days=0)
        mess = self.run_bg(procs=self.procs(wt))[str(clone.resolve())]["mess"]
        self.assertEqual(mess, [f"abnb: http server pid 111 serving {wt.resolve()} for 2d — stop it when done",
                                f"abnb: http server pid 222 serving {(wt / 'site').resolve()} for 3d — stop it when done"])

    def test_server_lines_are_capped_per_repo(self) -> None:
        _, clone = self.repo("abnb")
        wt = self.worktree(clone, "wt-yoga", days=0)
        many = [Proc(i, str(wt), ["python3", "-m", "http.server"], 2 * DAY) for i in range(10, 15)]
        mess = self.run_bg(procs=many)[str(clone.resolve())]["mess"]
        self.assertEqual((len(mess), mess[-1]), (4, "abnb: 2 more servers (see git worktree list, ps)"))

    def test_serving_directory_forms(self) -> None:
        for args, want in ((["-m", "http.server", "-d", "sub"], "/w/sub"), (["http.server", "--directory=/o"], "/o"), (["http.server", "-d"], "/w")):
            self.assertEqual(local_servers.serving_dir(Proc(1, "/w", args, 0)), want)

    def test_nothing_in_the_process_table_is_a_quiet_no_op(self) -> None:
        _, clone = self.repo("abnb")
        self.worktree(clone, "wt-yoga", days=0)
        self.assertEqual(self.run_bg(procs=[])[str(clone.resolve())]["mess"], [])


class ScanTest(MessBase):
    def fake_proc(self, procs: list[tuple[int, list[str], str, float]]) -> Path:
        root, hz = self.tmp / "proc", os.sysconf("SC_CLK_TCK")
        root.mkdir()
        (root / "stat").write_text("cpu 1 2 3\nbtime 1000000\n")
        for pid, args, cwd, started in procs:  # started: seconds after boot
            entry = root / str(pid)
            entry.mkdir()
            (entry / "cmdline").write_bytes(("\0".join(args) + "\0").encode())
            if cwd:
                (entry / "cwd").symlink_to(cwd)
            (entry / "stat").write_text(f"{pid} (my proc) S " + " ".join(["0"] * 18 + [str(int(started * hz))] + ["0"] * 5) + "\n")
        (root / "self").mkdir()
        return root

    def test_linux_proc_listing(self) -> None:
        wt = str(self.tmp)
        root = self.fake_proc([(10, ["python3", "-m", "http.server", "8000"], wt, 100), (11, ["sleep", "9"], wt, 100),
                               (12, ["python3", "-m", "http.server"], "", 100), (os.getpid(), ["python3", "-m", "http.server"], wt, 100)])
        found = REAL_SCAN(1000000 + 100 + 2 * DAY, root)
        self.assertEqual([(p.pid, p.cwd, p.args) for p in found], [(10, wt, ["python3", "-m", "http.server", "8000"])])
        self.assertAlmostEqual(found[0].age, 2 * DAY, delta=1)

    def test_macos_ps_and_lsof_best_effort(self) -> None:
        calls = []

        def run(cmd: list[str]) -> str:
            calls.append(cmd[0])
            if cmd[0] == "ps":
                return ("  123 2-03:04:05 python3 -m http.server 8000 --directory /x/y\n  456 00:10 python3 -m http.server\n"
                        "  789 3-00:00:00 /bin/bash\n  bad line\n")
            return "p123\nn/Users/me/github/wt\n"

        self.assertEqual(REAL_SCAN(0, self.tmp / "no-proc", run),
                         [Proc(123, "/Users/me/github/wt", ["python3", "-m", "http.server", "8000", "--directory", "/x/y"], 2 * DAY + 3 * 3600 + 4 * 60 + 5)])
        self.assertEqual(calls, ["ps", "lsof"])
        self.assertEqual(REAL_SCAN(0, self.tmp / "no-proc", lambda cmd: "" if cmd[0] == "ps" else self.fail("lsof without candidates")), [])

    def test_etime_forms_and_failures(self) -> None:
        self.assertEqual([local_servers.parse_etime(t) for t in ("05:10", "01:02:03", "2-03:04:05")], [310, 3723, 2 * DAY + 3 * 3600 + 4 * 60 + 5])

        def boom(cmd: list[str]) -> str:
            raise OSError("no ps")

        self.assertEqual(REAL_SCAN(0, self.tmp / "no-proc", boom), [])
        self.assertEqual(local_servers.run_cmd(["definitely-not-a-command-xyz"]), "")


class SessionStartMessTest(MessBase):
    def write(self, repos: dict) -> None:
        (self.home / ".agents").mkdir(exist_ok=True)
        (self.home / bg.STATUS).write_text(json.dumps({"version": 1, "updated": bg.now_iso(), "repos": repos}))

    def test_mess_lines_show_for_the_current_repo_only_and_its_sync_attention_does_not(self) -> None:
        here = self.tmp / "c"
        here.mkdir()
        self.write({str(here): {"attention": ["c (main): x"], "mess": ["c: worktree /w already merged — safe to remove (git worktree remove /w)"]},
                    "/r/a": {"attention": ["a: y"], "mess": []}})
        lines = bg.attention_lines(self.home, here)
        self.assertEqual([line.split(" (background")[0] for line in lines],
                         ["EpicSpine attention: c: worktree /w already merged — safe to remove (git worktree remove /w)"])

    def test_output_stays_capped_at_five(self) -> None:
        here = self.tmp / "c"
        here.mkdir()
        self.write({str(here): {"mess": [f"c: worktree /w{i} (b) idle 4d, not merged — merge it or remove it" for i in range(8)]}})
        self.assertEqual(len(bg.attention_lines(self.home, here)), 5)

    def test_the_abnb_scenario_end_to_end(self) -> None:
        bare, clone = self.repo("abnb-agent")
        old = self.worktree(clone, "wt-cdmx-yoga", days=2.5)
        self.worktree(clone, "wt-queretaro-shortlist", days=4)
        procs = [Proc(900, str(old), ["python3", "-m", "http.server", "8765"], 2.5 * DAY)]
        entry = self.run_bg(procs=procs)[str(clone.resolve())]
        self.assertEqual(entry["branches_pushed"], 2)
        self.assertEqual({"wt/wt-cdmx-yoga", "wt/wt-queretaro-shortlist"} <= self.remote_heads(bare), True)
        self.assertEqual(len(entry["mess"]), 2)  # the 4-day worktree and the server; the 2.5-day one is under the 3-day bar
        self.assertIn("idle 4d, not merged", entry["mess"][0])
        self.assertIn("http server pid 900 serving", entry["mess"][1])
        self.assertEqual(bg.attention_lines(self.home, self.tmp), [])  # a session elsewhere never sees abnb-agent's mess
        shown = bg.attention_lines(self.home, clone)
        self.assertEqual(len(shown), 2)
        self.assertTrue(all(line.endswith("(background sync; change nothing)") for line in shown))


if __name__ == "__main__":
    unittest.main()
