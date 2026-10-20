"""Machine-wide background sync: discovery, per-repo sync, status file, SessionStart lines, scheduling. Hermetic."""
from __future__ import annotations

import contextlib
import fcntl
import io
import json
import os
import plistlib
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import agents_block as ab  # noqa: E402
import background_sync as bg  # noqa: E402
import fake_bin  # noqa: E402
from _safe_env import safe_env  # noqa: E402
import local_servers  # noqa: E402
import rehook  # noqa: E402
import session_sync as ss  # noqa: E402
import sync_schedule as sched  # noqa: E402
import vendored_skill  # noqa: E402
from test_session_sync import GIT_ENV, SPINE  # noqa: E402

REAL_GIT = subprocess.run(["which", "git"], capture_output=True, text=True).stdout.strip()


def git(cwd: Path, *args: str, env: dict | None = None) -> str:
    proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True,
                          env=safe_env(**GIT_ENV, **(env or {})))
    return proc.stdout.strip()


def commit(cwd: Path, name: str, text: str, when: str | None = None) -> None:
    (cwd / name).parent.mkdir(parents=True, exist_ok=True)
    (cwd / name).write_text(text, encoding="utf-8")
    git(cwd, "add", "-A")
    dates = {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when} if when else {}
    git(cwd, "commit", "-qm", f"edit {name}", env=dates)


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-bg-")
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.home = self.tmp / "home"
        self.root = self.home / "github"
        self.root.mkdir(parents=True)
        self.bin = self.tmp / "fakebin"
        self.addCleanup(fake_bin.install(self.bin).stop)
        patch = mock.patch.dict(os.environ, {"HOME": str(self.home), "EPICSPINE_SYNC": "", "EPICSPINE_REPO_ROOTS": ""})
        patch.start()
        self.addCleanup(patch.stop)
        self.skill = ss.SKILL_DIR
        patch = mock.patch.object(local_servers, "scan", return_value=[])  # never read the real process table
        patch.start()
        self.addCleanup(patch.stop)

    def repo(self, name: str, seed: dict[str, str] | None = None, parent: Path | None = None) -> tuple[Path, Path]:
        """A bare origin plus a clone under ``parent`` (default ~/github), seeded on main."""
        bare, clone = self.tmp / f"{name}.git", (parent or self.root) / name
        clone.parent.mkdir(parents=True, exist_ok=True)
        git(self.tmp, "init", "-q", "--bare", "-b", "main", str(bare))
        git(self.tmp, "clone", "-q", str(bare), str(clone))
        git(clone, "checkout", "-q", "-B", "main")
        for rel, text in (seed or {"README.md": "x\n"}).items():
            commit(clone, rel, text)
        git(clone, "push", "-q", "-u", "origin", "main")
        return bare, clone

    def other(self, bare: Path, name: str) -> Path:
        path = self.tmp / name
        git(self.tmp, "clone", "-q", str(bare), str(path))
        return path

    def run_bg(self, **kw) -> dict:
        self.assertEqual(bg.run(dict(os.environ), self.home, self.skill, **kw), 0)
        return json.loads((self.home / bg.STATUS).read_text())["repos"]

    def entry(self, clone: Path) -> dict:
        return self.run_bg()[str(clone.resolve())]

    def shim_git(self, body: str) -> None:
        """A ``git`` first on PATH that runs ``body`` for some subcommands and otherwise the real git."""
        path = self.bin / "git"
        path.write_text(f'#!/bin/sh\n{body}\nexec {REAL_GIT} "$@"\n')
        path.chmod(path.stat().st_mode | stat.S_IEXEC)


class DiscoveryTest(Base):
    def test_default_roots_depth_two_and_skips(self) -> None:
        _, a = self.repo("a")
        _, nested = self.repo("b", parent=self.root / "org")
        _, deep = self.repo("c", parent=self.root / "x" / "y")  # depth 3: out of range
        wt = self.root / "a-wt"
        git(a, "worktree", "add", "-q", "-b", "side", str(wt))  # linked worktree: .git is a file
        (self.root / "plain").mkdir()
        (self.root / ".hidden").mkdir()
        (a / "sub" / "inner").mkdir(parents=True)  # never descended: a is a repo
        self.assertEqual(bg.discover(bg.roots(os.environ, self.home)), [a.resolve(), nested.resolve()])
        self.assertNotIn(deep.resolve(), bg.discover([self.root]))

    def test_env_roots_replace_defaults_and_missing_roots_are_ignored(self) -> None:
        _, a = self.repo("a")
        other = self.tmp / "elsewhere"
        _, b = self.repo("b", parent=other)
        env = {"EPICSPINE_REPO_ROOTS": os.pathsep.join([str(other), str(self.tmp / "nope")])}
        self.assertEqual(bg.roots(env, self.home), [other])
        self.assertEqual(bg.discover(bg.roots(env, self.home)), [b.resolve()])
        self.assertEqual([p.name for p in bg.roots({}, self.home)], ["github"])  # only existing defaults

    def test_symlinked_duplicates_are_listed_once(self) -> None:
        _, a = self.repo("a")
        (self.tmp / "link").symlink_to(self.root, target_is_directory=True)
        self.assertEqual(bg.discover([self.root, self.tmp / "link"]), [a.resolve()])

    def test_eligibility_origin_age_and_opt_outs(self) -> None:
        clock, now = ss.Clock(60), time.time()
        _, ok = self.repo("ok")
        self.assertTrue(bg.eligible(ok, clock, now))
        local = self.root / "local"
        git(self.tmp, "init", "-q", "-b", "main", str(local))
        commit(local, "a", "x")
        self.assertFalse(bg.eligible(local, clock, now))  # no origin
        _, old = self.repo("old")
        git(old, "commit", "-q", "--amend", "--no-edit", "--date=2020-01-01T00:00:00", env={"GIT_COMMITTER_DATE": "2020-01-01T00:00:00"})
        git(old, "push", "-q", "-f", "origin", "main")
        self.assertFalse(bg.eligible(old, clock, now))  # nothing within 90 days
        stamp = int(git(old, "log", "-1", "--format=%ct"))
        self.assertTrue(bg.eligible(old, clock, stamp + 80 * 86400))  # age is measured against `now`
        self.assertFalse(bg.eligible(old, clock, stamp + 100 * 86400))
        _, off = self.repo("off1")
        (off / ".epicspine-off").write_text("")
        _, off2 = self.repo("off2", {"AGENTS.md": "EpicSpine: off\n"})
        self.assertEqual([bg.eligible(p, clock, now) for p in (off, off2)], [False, False])

    def test_a_recent_remote_ref_makes_a_stale_checkout_eligible(self) -> None:
        bare, clone = self.repo("lag")
        git(clone, "commit", "-q", "--amend", "--no-edit", "--date=2020-01-01T00:00:00", env={"GIT_COMMITTER_DATE": "2020-01-01T00:00:00"})
        git(clone, "push", "-q", "-f", "origin", "main")
        other = self.other(bare, "o")
        commit(other, "n", "fresh")
        git(other, "push", "-q", "origin", "main")
        git(clone, "fetch", "-q", "origin")
        self.assertTrue(bg.eligible(clone, ss.Clock(60), time.time()))


class SyncTest(Base):
    def test_clean_behind_repo_is_fast_forwarded_and_recorded(self) -> None:
        bare, clone = self.repo("zenod")
        other = self.other(bare, "o")
        for i in range(3):
            commit(other, f"f{i}", "x")
        git(other, "push", "-q", "origin", "main")
        entry = self.entry(clone)
        self.assertEqual((entry["pulled"], entry["pushed"], entry["behind"], entry["ahead"], entry["branch"]), (3, 0, 0, 0, "main"))
        self.assertEqual(entry["attention"], [])
        self.assertEqual(git(clone, "rev-parse", "HEAD"), git(other, "rev-parse", "HEAD"))
        self.assertTrue(entry["last_run"].endswith("Z"))

    def test_committed_work_is_pushed_never_forced(self) -> None:
        bare, clone = self.repo("p")
        commit(clone, "mine", "x")
        entry = self.entry(clone)
        self.assertEqual((entry["pushed"], entry["ahead"]), (1, 0))
        self.assertEqual(git(bare, "rev-parse", "main"), git(clone, "rev-parse", "HEAD"))

    def test_pr_approval_policy_is_attention_not_a_push(self) -> None:
        bare, clone = self.repo("pr", {"AGENTS.md": "Integration policy: pr-approval\n"})
        before = git(bare, "rev-parse", "main")
        commit(clone, "mine", "x")
        entry = self.entry(clone)
        self.assertEqual(git(bare, "rev-parse", "main"), before)
        self.assertEqual(entry["attention"], ["pr (main): 1 unpushed commit(s) on main but Integration policy is pr-approval"])

    def test_diverged_dirty_behind_and_rejected_push_are_attention_and_change_nothing(self) -> None:
        bare, div = self.repo("div")
        _, dirty = self.repo("dirty")
        rej_bare, rej = self.repo("rej")
        for clone, name in ((div, "div"), (dirty, "dirty")):
            other = self.other(bare if name == "div" else self.tmp / "dirty.git", f"o-{name}")
            commit(other, "theirs", "x")
            git(other, "push", "-q", "origin", "main")
        commit(div, "ours", "x")
        (dirty / "README.md").write_text("edited\n")
        hook = rej_bare / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        commit(rej, "mine", "x")
        heads = {c: git(c, "rev-parse", "HEAD") for c in (div, dirty, rej)}
        repos = self.run_bg()
        self.assertEqual(repos[str(div.resolve())]["attention"], ["div (main): main diverged from origin/main (1 ahead, 1 behind)"])
        self.assertEqual(repos[str(dirty.resolve())]["attention"],
                         ["dirty (main): 1 commit(s) behind origin/main and the working tree has uncommitted changes"])
        self.assertEqual(repos[str(rej.resolve())]["attention"], ["rej (main): 1 unpushed commit(s) on main and the push failed"])
        self.assertEqual({c: git(c, "rev-parse", "HEAD") for c in heads}, heads)
        self.assertEqual((dirty / "README.md").read_text(), "edited\n")

    def test_worker_branches_are_backed_up_not_flagged(self) -> None:
        bare, clone = self.repo("w")
        git(clone, "checkout", "-q", "-b", "wt-task")
        commit(clone, "mine", "x")
        entry = self.entry(clone)
        self.assertEqual((entry["attention"], entry["branches_pushed"]), ([], 1))
        self.assertEqual(git(bare, "rev-parse", "wt-task"), git(clone, "rev-parse", "wt-task"))

    def test_gate_installed_only_where_epicspine_is_used_and_no_blocks_are_written(self) -> None:
        with_spine = self.repo("spine", {"docs/EPIC.md": SPINE, "AGENTS.md": "Root spine: docs/EPIC.md. Read it.\n"})[1]
        plain = self.repo("plain")[1]
        foreign = self.repo("foreign", {"AGENTS.md": "Root spine: none. Read x\n<!-- epicspine:begin repo-1 -->\nx\n<!-- epicspine:end -->\n"})[1]
        hook = foreign / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh\necho mine\n")
        self.run_bg()
        self.assertIn(ab.HOOK_MARK, (with_spine / ".git" / "hooks" / "pre-commit").read_text())
        self.assertFalse((plain / ".git" / "hooks" / "pre-commit").exists())
        self.assertEqual(hook.read_text(), "#!/bin/sh\necho mine\n")  # foreign hook kept
        self.assertFalse((plain / "AGENTS.md").exists())  # blocks are the SessionStart's job, never unattended
        self.assertEqual(git(plain, "status", "--porcelain"), "")

    def test_opted_out_repo_gets_no_hook_and_no_entry(self) -> None:
        _, off = self.repo("off", {"AGENTS.md": "Root spine: none. Read x\n<!-- epicspine:begin repo-1 -->\nx\n<!-- epicspine:end -->\n", ".epicspine-off": ""})
        self.assertEqual(self.run_bg(), {})
        self.assertFalse((off / ".git" / "hooks" / "pre-commit").exists())

    def test_old_vendored_copy_is_attention_every_run(self) -> None:
        _, clone = self.repo("v", {"skills/epic-spine/SKILL.md": "---\nname: epic-spine\n---\nx\n", "skills/epic-spine/VERSION": "2026.10.01\n"})
        for _ in range(2):  # not throttled, so it never flickers off between runs
            att = self.entry(clone)["attention"]
            self.assertEqual(len(att), 1)
            self.assertIn("v: old copy of the epic-spine skill at skills/epic-spine (2026.10.01", att[0])

    def test_one_failing_repo_does_not_stop_the_rest(self) -> None:
        _, a = self.repo("a")
        bare, b = self.repo("b")
        other = self.other(bare, "o")
        commit(other, "n", "x")
        git(other, "push", "-q", "origin", "main")
        real = bg.sync_repo

        def boom(top, *args):
            if top.name == "a":
                raise RuntimeError("kaput")
            return real(top, *args)

        with mock.patch.object(bg, "sync_repo", boom):
            repos = self.run_bg()
        self.assertIn("a: background sync failed (kaput)", repos[str(a.resolve())]["attention"][0])
        self.assertEqual(repos[str(b.resolve())]["pulled"], 1)


class BoundsTest(Base):
    def test_never_prompts(self) -> None:
        self.repo("a")
        seen = self.tmp / "env.txt"
        self.shim_git(f'case "$*" in *fetch*) echo "$GIT_TERMINAL_PROMPT|$GIT_SSH_COMMAND" > {seen};; esac')
        self.run_bg()
        prompt, ssh = seen.read_text().strip().split("|")
        self.assertEqual(prompt, "0")
        self.assertIn("BatchMode=yes", ssh)

    def test_a_hung_fetch_is_cut_off_at_the_per_repo_budget(self) -> None:
        _, a = self.repo("a")
        self.shim_git('case "$*" in *fetch*) exec sleep 30;; esac')
        t0 = time.monotonic()
        with mock.patch.object(bg, "REPO_SECONDS", 1.5):
            entry = self.entry(a)
        self.assertLess(time.monotonic() - t0, 12)
        self.assertEqual((entry["pulled"], entry["pushed"], entry["attention"]), (0, 0, []))

    def test_repo_clock_never_exceeds_twenty_seconds_or_the_total(self) -> None:
        _, a = self.repo("a")
        caps = []

        def spy(top, clock, **kw):
            caps.append(clock.cap(1000))
            return []

        with mock.patch.object(bg.repo_sync, "sync", spy):
            self.run_bg()
        self.assertLessEqual(caps[0], 20.0)
        self.assertEqual(bg.REPO_SECONDS, 20.0)
        self.assertEqual(bg.TOTAL_SECONDS, 300.0)

    def test_out_of_total_time_keeps_old_entries_and_retries_them_first(self) -> None:
        _, a = self.repo("a")
        _, b = self.repo("b")
        first = self.run_bg()
        order = []
        with mock.patch.object(bg, "TOTAL_SECONDS", 0.0), mock.patch.object(bg, "sync_repo", side_effect=lambda *a_: order.append(a_[0]) or {}):
            again = self.run_bg()
        self.assertEqual(again, first)  # nothing synced, last known entries kept
        self.assertEqual(order, [])
        # least recently synced goes first
        data = json.loads((self.home / bg.STATUS).read_text())
        data["repos"][str(b.resolve())]["last_run"] = "2020-01-01T00:00:00Z"
        (self.home / bg.STATUS).write_text(json.dumps(data))
        with mock.patch.object(bg, "sync_repo", side_effect=lambda *a_: order.append(a_[0].name) or {"name": a_[0].name, "attention": []}):
            self.run_bg()
        self.assertEqual(order, ["b", "a"])

    def test_vanished_repos_drop_out_of_the_status_file(self) -> None:
        _, a = self.repo("a")
        self.assertEqual(list(self.run_bg()), [str(a.resolve())])
        import shutil
        shutil.rmtree(a)
        self.assertEqual(self.run_bg(), {})

    def test_a_held_lock_means_another_run_is_in_progress(self) -> None:
        self.repo("a")
        lock = self.home / bg.LOCK
        lock.parent.mkdir(parents=True)
        with open(lock, "w") as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            with mock.patch.object(bg, "sync_repo", side_effect=AssertionError("overlap")):
                self.assertEqual(bg.run(dict(os.environ), self.home, self.skill), 0)
        self.assertFalse((self.home / bg.STATUS).exists())
        self.assertEqual(len(self.run_bg()), 1)  # released: runs again

    def test_off_switch(self) -> None:
        self.repo("a")
        self.assertEqual(bg.run({**os.environ, "EPICSPINE_SYNC": "off"}, self.home, self.skill), 0)
        self.assertFalse((self.home / bg.STATUS).exists())

    def test_the_real_process_is_silent_and_writes_the_status_file(self) -> None:
        bare, clone = self.repo("a")
        other = self.other(bare, "o")
        commit(other, "n", "x")
        git(other, "push", "-q", "origin", "main")
        for args, quiet in (([], True), (["-v"], False)):
            proc = subprocess.run([sys.executable, "-B", str(SCRIPTS / "background_sync.py"), *args], capture_output=True, text=True, timeout=120,
                                  env=safe_env(EPICSPINE_REPO_ROOTS=str(self.root)))
            self.assertEqual((proc.returncode, proc.stderr, proc.stdout == ""), (0, "", quiet))
        self.assertEqual(git(clone, "rev-parse", "HEAD"), git(other, "rev-parse", "HEAD"))
        self.assertEqual(json.loads((self.home / bg.STATUS).read_text())["skill"], ss.read_version(self.skill))


class SessionStartLinesTest(Base):
    def write(self, repos: dict, updated: str | None = None) -> None:
        (self.home / ".agents").mkdir(exist_ok=True)
        (self.home / bg.STATUS).write_text(json.dumps({"version": 1, "updated": updated or bg.now_iso(), "repos": repos}))

    def test_no_file_or_nothing_wrong_prints_nothing(self) -> None:
        self.assertEqual(bg.attention_lines(self.home, self.tmp), [])
        self.write({"/r/a": {"attention": []}})
        self.assertEqual(bg.attention_lines(self.home, self.tmp), [])

    def test_any_repo_but_the_current_one_is_listed_with_why(self) -> None:
        here = self.tmp / "c"
        (here / "deeper").mkdir(parents=True)
        self.write({"/r/a": {"attention": ["a (main): main diverged from origin/main (1 ahead, 1 behind)"]},
                    "/r/b": {"attention": ["b: old copy of the epic-spine skill at skills/epic-spine (1, installed 2)"]},
                    str(here): {"attention": ["c (main): x"]}})
        lines = bg.attention_lines(self.home, here / "deeper")  # a session anywhere inside c: c itself is left to the live check
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(line.startswith("EpicSpine attention: ") for line in lines))
        self.assertIn("a (main): main diverged", lines[0])
        self.assertIn("b: old copy", lines[1])
        self.assertEqual(len(bg.attention_lines(self.home, self.tmp)), 3)

    def test_at_most_five_then_n_more(self) -> None:
        self.write({f"/r/{i}": {"attention": [f"r{i} (main): stuck"]} for i in range(8)})
        lines = bg.attention_lines(self.home, self.tmp)
        self.assertEqual(len(lines), 6)
        self.assertEqual(lines[-1].split(" (see")[0], "EpicSpine attention: 3 more")

    def test_a_job_that_stopped_running_is_reported(self) -> None:
        self.write({}, updated="2026-01-01T00:00:00Z")
        lines = bg.attention_lines(self.home, self.tmp)
        self.assertEqual(len(lines), 1)
        self.assertIn("has not run since 2026-01-01T00:00:00Z", lines[0])
        self.assertIn("check-global", lines[0])

    def test_session_start_prints_them_and_the_off_switch_silences_them(self) -> None:
        self.write({"/r/a": {"attention": ["a (main): main diverged from origin/main (1 ahead, 1 behind)"]}})
        with mock.patch.object(ss, "sync_skill", return_value=None):
            notes = ss.run(dict(os.environ), home=self.home, cwd=self.tmp, clock=ss.Clock(30), skill_dir=self.skill)
            self.assertEqual([n.split(" (background")[0] for n in notes if "diverged" in n],
                             ["EpicSpine attention: a (main): main diverged from origin/main (1 ahead, 1 behind)"])
            self.assertEqual(ss.run({"EPICSPINE_SYNC": "off"}, home=self.home, cwd=self.tmp, clock=ss.Clock(30)), [])

    def test_end_to_end_status_then_hook_line(self) -> None:
        bare, div = self.repo("div")
        other = self.other(bare, "o")
        commit(other, "t", "x")
        git(other, "push", "-q", "origin", "main")
        commit(div, "o", "x")
        self.run_bg()
        self.assertEqual(len(bg.attention_lines(self.home, self.tmp)), 1)
        self.assertEqual(bg.attention_lines(self.home, div), [])  # the live check owns the current repo


class CronTest(Base):
    def setUp(self) -> None:
        super().setUp()
        self.line = sched.cron_line(self.skill)

    def tab(self) -> str:
        return fake_bin.crontab_text(self.bin)

    def test_exact_line(self) -> None:
        self.assertEqual(self.line, f'*/15 * * * * python3 "{self.skill}/scripts/background_sync.py" >/dev/null 2>&1 # epicspine-background-sync')

    def test_install_is_idempotent_and_preserves_other_entries(self) -> None:
        foreign = "MAILTO=me@example.com\n20 5 * * * /usr/bin/backup --all\n"
        (self.bin / "state").mkdir(parents=True, exist_ok=True)
        (self.bin / "state" / "crontab").write_text(foreign)
        self.assertEqual(sched.cron_install(self.skill), "installed")
        self.assertEqual(self.tab(), foreign + self.line + "\n")
        self.assertEqual(sched.cron_install(self.skill), "current")
        self.assertEqual(self.tab().count("epicspine-background-sync"), 1)
        self.assertEqual(sched.cron_state(self.skill), "current")

    def test_a_stale_entry_is_replaced_not_duplicated(self) -> None:
        (self.bin / "state").mkdir(parents=True, exist_ok=True)
        (self.bin / "state" / "crontab").write_text('*/5 * * * * python3 "/old/background_sync.py" # epicspine-background-sync\nkeep me\n')
        self.assertEqual(sched.cron_state(self.skill), "stale")
        self.assertEqual(sched.cron_install(self.skill), "updated")
        self.assertEqual(self.tab(), "keep me\n" + self.line + "\n")

    def test_no_crontab_yet_is_fine_and_an_unreadable_one_is_never_overwritten(self) -> None:
        self.assertEqual(sched.read_cron(), "")
        self.assertEqual(sched.cron_state(self.skill), "missing")
        (self.bin / "state" / "crontab").write_text("precious\n")
        (self.bin / "state" / "fail-read").write_text("")
        self.assertEqual(sched.cron_install(self.skill), "error: cannot read crontab")
        self.assertEqual(sched.cron_remove(), "error: cannot read crontab")
        (self.bin / "state" / "fail-read").unlink()
        self.assertEqual(self.tab(), "precious\n")

    def test_write_failure_is_an_error(self) -> None:
        (self.bin / "state").mkdir(parents=True, exist_ok=True)
        (self.bin / "state" / "fail-write").write_text("")
        self.assertEqual(sched.cron_install(self.skill), "error: crontab write failed")

    def test_remove_takes_only_ours(self) -> None:
        sched.cron_install(self.skill)
        (self.bin / "state" / "crontab").write_text("a b c\n" + self.line + "\n")
        self.assertEqual(sched.cron_remove(), "removed")
        self.assertEqual(self.tab(), "a b c\n")
        self.assertEqual(sched.cron_remove(), "absent")

    def test_apply_reports_and_respects_the_home_and_off_guards(self) -> None:
        self.assertEqual(sched.apply("check", self.home, self.skill), ("missing (user crontab, every 15 min)", 1))
        self.assertEqual(sched.apply("install", self.home, self.skill)[1], 0)
        self.assertEqual(sched.apply("check", self.home, self.skill), ("scheduled (user crontab, every 15 min)", 0))
        self.assertEqual(sched.apply("uninstall", self.home, self.skill)[0], "removed (user crontab, every 15 min)")
        calls = len(fake_bin.calls(self.bin))
        self.assertEqual(sched.apply("install", self.tmp / "elsewhere", self.skill), ("skipped (--home override)", 0))
        self.assertEqual(sched.apply("install", self.home, self.skill, {"EPICSPINE_SYNC": "off"})[0].split(" (")[0], "not installed")
        self.assertEqual(len(fake_bin.calls(self.bin)), calls)  # neither touched crontab


class LaunchdTest(Base):
    def setUp(self) -> None:
        super().setUp()
        patch = mock.patch.object(sched, "kind", return_value="launchd")
        patch.start()
        self.addCleanup(patch.stop)
        self.plist = sched.plist_path(self.home)

    def test_plist_is_valid_and_points_at_the_installed_script(self) -> None:
        data = plistlib.loads(sched.plist_text(self.skill).encode())
        self.assertEqual(data["Label"], "dev.epicspine.sync")
        self.assertEqual(data["StartInterval"], 900)
        self.assertTrue(data["RunAtLoad"])
        self.assertEqual(data["ProgramArguments"], ["/usr/bin/env", "python3", f"{self.skill}/scripts/background_sync.py"])
        self.assertIn("/opt/homebrew/bin", data["EnvironmentVariables"]["PATH"])
        self.assertEqual(self.plist, self.home / "Library" / "LaunchAgents" / "dev.epicspine.sync.plist")

    def test_install_bootstraps_once_then_is_current(self) -> None:
        self.assertEqual(sched.launchd_install(self.home, self.skill), "installed")
        self.assertEqual(self.plist.read_text(), sched.plist_text(self.skill))
        self.assertIn(f"launchctl bootstrap gui/{os.getuid()} {self.plist}", fake_bin.calls(self.bin))
        before = [c for c in fake_bin.calls(self.bin) if "bootstrap" in c]
        self.assertEqual(sched.launchd_install(self.home, self.skill), "current")
        self.assertEqual([c for c in fake_bin.calls(self.bin) if "bootstrap" in c], before)
        self.assertEqual(sched.launchd_state(self.home, self.skill), "current")

    def test_not_loaded_is_reloaded_and_a_stale_plist_is_rewritten(self) -> None:
        sched.launchd_install(self.home, self.skill)
        (self.bin / "state" / "loaded").unlink()
        self.assertEqual(sched.launchd_state(self.home, self.skill), "not loaded")
        self.assertEqual(sched.launchd_install(self.home, self.skill), "loaded")
        self.plist.write_text("old")
        self.assertEqual(sched.launchd_state(self.home, self.skill), "stale")
        self.assertEqual(sched.launchd_install(self.home, self.skill), "installed")
        self.assertTrue(any(c.startswith("launchctl bootout") for c in fake_bin.calls(self.bin)))

    def test_falls_back_to_load_when_bootstrap_fails(self) -> None:
        (self.bin / "state").mkdir(parents=True, exist_ok=True)
        (self.bin / "state" / "no-bootstrap").write_text("")
        self.assertEqual(sched.launchd_install(self.home, self.skill), "installed")
        self.assertIn(f"launchctl load -w {self.plist}", fake_bin.calls(self.bin))

    def test_uninstall_unloads_and_deletes(self) -> None:
        sched.launchd_install(self.home, self.skill)
        self.assertEqual(sched.launchd_remove(self.home), "removed")
        self.assertFalse(self.plist.exists())
        self.assertFalse((self.bin / "state" / "loaded").exists())
        self.assertEqual(sched.launchd_remove(self.home), "absent")


class InstallGlobalTest(Base):
    """install-global / check-global / uninstall-global drive the schedule; --home overrides never touch it."""

    def setUp(self) -> None:
        super().setUp()
        (self.home / ".claude").mkdir()
        patch = mock.patch("codex_hooks.list_hooks", return_value=None)
        patch.start()
        self.addCleanup(patch.stop)

    def cmd(self, *args: str) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = ab.main(list(args))
        return code, buf.getvalue()

    def test_install_check_uninstall(self) -> None:
        line = sched.cron_line(self.skill)
        code, out = self.cmd("check-global")
        self.assertEqual(code, 1)
        self.assertIn("background sync: missing (user crontab, every 15 min)", out)
        code, out = self.cmd("install-global")
        self.assertIn("background sync: installed (user crontab, every 15 min)", out)
        self.assertEqual(fake_bin.crontab_text(self.bin), line + "\n")
        self.assertIn("background sync: current", self.cmd("install-global")[1])
        code, out = self.cmd("check-global")
        self.assertEqual(code, 0, out)
        self.assertIn("background sync: scheduled", out)
        self.assertIn("background sync: removed", self.cmd("uninstall-global")[1])
        self.assertEqual(fake_bin.crontab_text(self.bin), "")

    def test_home_override_no_hooks_only_and_off_switch_leave_the_crontab_alone(self) -> None:
        (self.tmp / "other" / ".claude").mkdir(parents=True)
        out = self.cmd("install-global", "--home", str(self.tmp / "other"))[1]
        self.assertIn("background sync: skipped (--home override)", out)
        self.cmd("install-global", "--no-hooks")
        self.cmd("install-global", "--only", "claude-code")
        with mock.patch.dict(os.environ, {"EPICSPINE_SYNC": "off"}):
            self.assertIn("background sync: not installed (EPICSPINE_SYNC=off)", self.cmd("install-global")[1])
        self.assertEqual(fake_bin.crontab_text(self.bin), "")

    def test_the_cli_script(self) -> None:
        run = lambda *a: subprocess.run([sys.executable, "-B", str(SCRIPTS / "sync_schedule.py"), *a], capture_output=True, text=True, timeout=60)  # noqa: E731
        self.assertEqual((run("check").returncode, run("ensure").stdout.split(" (")[0]), (1, "background sync: installed"))
        self.assertEqual(run("ensure").stdout.split(" (")[0], "background sync: current")
        self.assertEqual(run("uninstall").stdout.split(" (")[0], "background sync: removed")
        self.assertEqual(run("bogus").returncode, 2)


class RehookScheduleTest(Base):
    def ensure(self, updated: bool = False, env: dict | None = None) -> str | None:
        return rehook.ensure_schedule(env or {}, self.home, self.skill, updated)

    def test_a_missing_entry_is_installed_once_and_noted(self) -> None:
        self.assertEqual(self.ensure(), "background sync scheduled")
        self.assertEqual(fake_bin.crontab_text(self.bin), sched.cron_line(self.skill) + "\n")
        self.assertIsNone(self.ensure())
        self.assertIsNone(self.ensure(updated=True))  # still current: re-ensured by the new script, silently

    def test_a_stale_entry_after_the_skill_moved_is_rewritten(self) -> None:
        (self.bin / "state").mkdir(parents=True, exist_ok=True)
        (self.bin / "state" / "crontab").write_text('*/15 * * * * python3 "/old/skill/scripts/background_sync.py" # epicspine-background-sync\n')
        self.assertEqual(self.ensure(), "background sync scheduled")
        self.assertEqual(fake_bin.crontab_text(self.bin), sched.cron_line(self.skill) + "\n")

    def test_missing_is_retried_at_most_every_ten_minutes_unless_updated(self) -> None:
        (self.bin / "state").mkdir(parents=True, exist_ok=True)
        (self.bin / "state" / "fail-write").write_text("")  # install keeps failing
        self.assertEqual(self.ensure(), "background sync scheduled")  # it tried
        calls = len(fake_bin.calls(self.bin))
        self.assertIsNone(self.ensure())
        self.assertEqual(len(fake_bin.calls(self.bin)), calls + 1)  # only the cheap `crontab -l` check
        self.ensure(updated=True)
        self.assertGreater(len(fake_bin.calls(self.bin)), calls + 1)

    def test_off_switch_foreign_home_and_unreadable_crontab_do_nothing(self) -> None:
        self.assertIsNone(self.ensure(env={"EPICSPINE_SYNC": "off"}))
        self.assertIsNone(rehook.ensure_schedule({}, self.tmp / "other", self.skill, True))
        (self.bin / "state").mkdir(parents=True, exist_ok=True)
        (self.bin / "state" / "fail-read").write_text("")
        self.assertIsNone(self.ensure(updated=True))
        self.assertEqual(fake_bin.crontab_text(self.bin), "")

    def test_rehook_run_adds_the_note_to_the_hook_line(self) -> None:
        cfg = self.tmp / "cfg"
        cfg.mkdir()
        self.assertEqual(rehook.run({"CLAUDE_CONFIG_DIR": str(cfg)}, self.home, self.skill, False), "background sync scheduled")
        self.assertIsNone(rehook.run({"CLAUDE_CONFIG_DIR": str(cfg)}, self.home, self.skill, False))


if __name__ == "__main__":
    unittest.main()
