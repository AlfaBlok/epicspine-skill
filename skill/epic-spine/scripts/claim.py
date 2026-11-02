#!/usr/bin/env python3
"""Claim a ledger row before working on it (agent_team E63-S3/S4: one claim per row, no silent death).

    spines.py --claim ROW --by WHO [--repo DIR] [--spine PATH] [--lease-min N] [--renew | --release] [--note TEXT]

The claim is written into the row itself, in one commit pushed to the repo's integration branch, so every entry point
(console wake, T3 thread, desk, subagent, any host) meets the same lock: the git push. The row's Owner / Assignment
cell becomes ``WHO — claimed <UTC>, lease until <UTC>`` and its Status ``active``. A live claim by someone else is
refused (exit 3) and the message names the holder; a closed row (done, superseded, cancelled) is refused (exit 4).
The worker's later commits that name the row renew the lease (the console reads them); ``--renew`` extends it by hand,
``--release`` gives the row back (Owner ``unassigned``, Status ``ready``).

It works on a fresh partial clone of the checkout's ``origin`` (never the caller's working tree, which may be dirty or
on a worktree branch). A push rejected as non-fast-forward re-fetches, re-reads the row and re-checks the claim, up to
three times, so two claims racing from two hosts end with exactly one holder.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

LEASE = re.compile(r"\s*[—-]+\s*claimed (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z), lease until (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)")
CLOSED = re.compile(r"^\s*\**\s*(done|superseded|cancell?ed|moved)\b", re.I)
SPINE_DIRS = ("docs/spines", "docs")


def now() -> dt.datetime:
    fixed = os.environ.get("EPICSPINE_CLAIM_NOW")  # tests
    return dt.datetime.strptime(fixed, "%Y-%m-%dT%H:%MZ").replace(tzinfo=dt.timezone.utc) if fixed else dt.datetime.now(dt.timezone.utc)


def stamp(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%MZ")


def parse_stamp(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ").replace(tzinfo=dt.timezone.utc)


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=check)


def split(line: str) -> list[str]:
    return re.split(r"(?<!\\)\|", line)


def find_row(clone: Path, row: str, spine: str | None) -> tuple[Path, int, list[str], list[str]] | None:
    """(file, line index, header cells, row cells) of the ledger row ``row`` (first match; ``spine`` narrows it)."""
    files = [clone / spine] if spine else sorted(p for d in SPINE_DIRS for p in (clone / d).glob("*.md") if p.is_file())
    for f in files:
        if not f.is_file():
            continue
        lines = f.read_text(encoding="utf-8").split("\n")
        header: list[str] = []
        for i, line in enumerate(lines):
            if not line.strip().startswith("|"):
                header = []
                continue
            cells = split(line)
            if not header:
                header = [c.strip() for c in cells]
                continue
            if set(line.strip()) <= set("|-: "):
                continue
            if len(cells) > 2 and cells[1].strip() == row:
                return f, i, header, cells
    return None


def col(header: list[str], *names: str) -> int:
    low = [h.lower() for h in header]
    for n in names:
        for i, h in enumerate(low):
            if h == n or h.startswith(n):
                return i
    return -1


def holder_of(owner_cell: str) -> tuple[str, dt.datetime, dt.datetime] | None:
    m = LEASE.search(owner_cell)
    if not m:
        return None
    return owner_cell[: m.start()].strip(), parse_stamp(m.group(1)), parse_stamp(m.group(2))


def attempt(clone: Path, a: argparse.Namespace, branch: str) -> tuple[int, str]:
    hit = find_row(clone, a.row, a.spine)
    if not hit:
        return 5, f"row {a.row} not found in {a.spine or 'the spines'} on origin/{branch}"
    f, i, header, cells = hit
    so, oo = col(header, "status", "state"), col(header, "owner", "assignee")
    if so < 0 or oo < 0:
        return 5, f"row {a.row}'s table has no Status or Owner column"
    status, owner = cells[so].strip(), cells[oo].strip()
    if CLOSED.match(status) and not a.release:
        return 4, f"row {a.row} is closed ({status[:80]}); nothing claimed"
    t = now()
    held = holder_of(owner)
    if held and held[2] > t and held[0] != a.by:
        return 3, f"row {a.row} is claimed by {held[0]} until {stamp(held[2])} (since {stamp(held[1])}); not claimed"
    if a.release:
        if not held or held[0] != a.by:
            return 3, f"row {a.row} is not claimed by {a.by}; nothing released"
        cells[oo] = " unassigned "
        if not CLOSED.match(status):
            cells[so] = " ready "
        what = f"Release {a.row}: {a.by}"
    else:
        since = held[1] if held and held[0] == a.by and a.renew else t
        until = t + dt.timedelta(minutes=a.lease_min)
        cells[oo] = f" {a.by} — claimed {stamp(since)}, lease until {stamp(until)} ".replace("|", "/")
        if not re.match(r"^\s*active\b", status, re.I):
            cells[so] = " active "
        what = f"{'Renew' if a.renew else 'Claim'} {a.row}: {a.by} (lease until {stamp(until)})"
    lines = f.read_text(encoding="utf-8").split("\n")
    lines[i] = "|".join(cells)
    f.write_text("\n".join(lines), encoding="utf-8")
    rel = str(f.relative_to(clone))
    git(clone, "add", rel)
    body = (a.note + "\n\n") if a.note else ""
    git(clone, "commit", "-q", "--no-verify", "-m", what, "-m", f"{body}EpicSpine claim (agent_team E63-S3): {rel}")
    push = git(clone, "push", "-q", "origin", f"HEAD:{branch}", check=False)
    if push.returncode != 0:
        return 75, push.stderr.strip() or "push rejected"
    return 0, f"{what}: {rel} @ {git(clone, 'rev-parse', '--short', 'HEAD').stdout.strip()}"


def claim(a: argparse.Namespace) -> int:
    repo = Path(a.repo).resolve()
    url = git(repo, "remote", "get-url", "origin", check=False).stdout.strip()
    if not url:
        print(f"claim: {repo} has no origin remote", file=sys.stderr)
        return 2
    branch = a.branch or "main"
    name = git(repo, "config", "user.name", check=False).stdout.strip() or "EpicSpine claim"
    mail = git(repo, "config", "user.email", check=False).stdout.strip() or "claim@epicspine.local"
    with tempfile.TemporaryDirectory(prefix="epicspine-claim-") as tmp:
        clone = Path(tmp) / "repo"
        for n in range(3):
            if clone.exists():
                git(clone, "fetch", "-q", "origin", branch)
                git(clone, "reset", "-q", "--hard", f"origin/{branch}")
            else:
                c = subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--branch", branch, url, str(clone)], capture_output=True, text=True)
                if c.returncode != 0:
                    print(f"claim: clone of {url} failed: {c.stderr.strip()}", file=sys.stderr)
                    return 2
                git(clone, "config", "user.name", name)
                git(clone, "config", "user.email", mail)
            code, msg = attempt(clone, a, branch)
            if code != 75:
                print(msg, file=sys.stderr if code else sys.stdout)
                if code == 0 and not a.no_pull:
                    git(repo, "pull", "-q", "--ff-only", check=False)  # the caller's checkout sees it too (best effort)
                return code
        print(f"claim: row {a.row}: the push was rejected three times (others writing); try again", file=sys.stderr)
        return 75


def add_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--by", help="who claims: a run id, thread id or persona (required with --claim)")
    p.add_argument("--spine", help="the spine file holding the row (repo-relative), when the code is not unique")
    p.add_argument("--lease-min", type=int, default=120, help="lease length in minutes (default 120); commits naming the row renew it")
    p.add_argument("--renew", action="store_true", help="extend your own claim")
    p.add_argument("--release", action="store_true", help="give your claim back (row to ready)")
    p.add_argument("--note", default="", help="a line for the commit body")
    p.add_argument("--branch", help="integration branch (default main)")
    p.add_argument("--no-pull", action="store_true", help="do not fast-forward the caller's checkout afterwards")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("row")
    p.add_argument("--repo", default=".")
    add_args(p)
    a = p.parse_args()
    if not a.by:
        p.error("--by is required")
    return claim(a)


if __name__ == "__main__":
    sys.exit(main())
