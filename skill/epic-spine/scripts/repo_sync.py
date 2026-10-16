#!/usr/bin/env python3
"""SessionStart repo steps (called by session_sync.run): keep the current git repo in sync and set up.

1. sync: fetch origin; clean + only behind -> fast-forward; ahead on the integration branch -> push
   (fast-forward only; never under ``Integration policy: pr-approval``); diverged or dirty-and-behind on
   the integration branch -> change nothing and return an ``EpicSpine attention:`` line.
2. install: a repo with a root spine but no current AGENTS.md EpicSpine block gets one (agents_block.py
   install), and a root spine without ``## Operating Learnings`` gets an empty section. Both stay
   uncommitted; one line asks the agent to commit them per Integration policy.
Repos with no discoverable root spine are left alone. Stdlib only; never raises.
"""

from __future__ import annotations

import contextlib
import io
import re
from pathlib import Path

from session_sync import Clock, git, out

LEARNINGS = ("## Operating Learnings\n\n**Always** (every task; read in full at bind):\n\n- (none yet)\n\n"
             "**Scoped index** (follow only when the trigger matches):\n\n- (none yet)\n\n")
LEARNINGS_RE = re.compile(r"^## Operating Learnings[ \t]*$", re.MULTILINE)
STATE_RE = re.compile(r"^## Current State[ \t]*$", re.MULTILINE)
FIELD = r"^[ \t>*_-]*{}[*_ ]*:[*_ \t`]*([^\s`*]+)"
BUSY = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply")
NAMED = re.compile(r"(?i)(epic|spine)")


def field(text: str, name: str) -> str | None:
    match = re.search(FIELD.format(name), text, re.MULTILINE | re.IGNORECASE)
    return match.group(1) if match else None


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def repo_text(top: Path, spine: Path | None = None) -> str:
    return read(top / "AGENTS.md") + "\n" + (read(spine) if spine else "")


def find_spine(top: Path, clock: Clock) -> Path | None:
    """The root spine: the AGENTS.md block's ``Root spine:`` file if it exists, else the one tracked
    epic/spine-named .md (depth <= 3) with a Current State that is not a child; ambiguity -> None."""
    block = field(read(top / "AGENTS.md"), "Root spine")
    if block and (top / block.rstrip(".")).is_file():
        return top / block.rstrip(".")
    listing = out(git(["ls-files", "*.md"], top, clock, 3)) or ""
    found: list[tuple[bool, Path]] = []
    for rel in listing.splitlines():
        path = Path(rel)
        if len(path.parts) > 3 or not NAMED.search(path.name):
            continue
        text = read(top / rel)
        kind, parent, root = (field(text, n) or "" for n in ("Spine Type", "Parent spine", "Root spine"))
        if not STATE_RE.search(text) or kind.lower() in ("child", "branch", "ticket") or parent.lower() not in ("", "none") \
                or root.lower() not in ("", "self", "none", rel.lower()):
            continue
        found.append((kind.lower() == "root", top / rel))
    roots = [p for is_root, p in found if is_root]
    pick = roots or [p for _, p in found]
    return pick[0] if len(pick) == 1 else None


def ensure_learnings(spine: Path) -> bool:
    text = read(spine)
    state = STATE_RE.search(text)
    if not state or LEARNINGS_RE.search(text):
        return False
    spine.write_text(text[: state.start()] + LEARNINGS + text[state.start():], encoding="utf-8")
    return True


def install(top: Path, clock: Clock) -> list[str]:
    spine = find_spine(top, clock)
    if spine is None:
        return []
    import agents_block as ab
    did: list[str] = []
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            if ab.check(top) != 0:
                ab.install(top, spine.relative_to(top).as_posix())
                did.append("AGENTS.md block")
    except (Exception, SystemExit):
        pass
    if ensure_learnings(spine):
        did.append(f"Operating Learnings in {spine.relative_to(top).as_posix()}")
    if not did:
        return []
    return [f"EpicSpine setup: installed {' and '.join(did)} in {top.name}, uncommitted: commit "
            "them per this repo's Integration policy."]


def sync(top: Path, clock: Clock) -> list[str]:
    def run(*args: str, seconds: float = 4.0) -> str | None:
        return out(git(list(args), top, clock, seconds))

    branch = run("symbolic-ref", "--short", "-q", "HEAD")
    if not branch or run("remote", "get-url", "origin") is None or run("fetch", "--quiet", "origin", seconds=5) is None:
        return []
    if any((top / (run("rev-parse", "--git-path", name) or "-")).exists() for name in BUSY):
        return []
    counts = (run("rev-list", "--left-right", "--count", f"HEAD...origin/{branch}") or "").split()
    if len(counts) != 2 or counts == ["0", "0"]:
        return []
    ahead, behind = int(counts[0]), int(counts[1])
    spine = find_spine(top, clock)
    text = repo_text(top, spine)
    integration = field(text, "Integration branch")
    if not integration:
        head = run("symbolic-ref", "--short", "-q", "refs/remotes/origin/HEAD") or ""
        integration = head.removeprefix("origin/") or ("main" if run("rev-parse", "--verify", "-q", "origin/main") else "master")
    mine, dirty = branch == integration, bool(run("status", "--porcelain", "--untracked-files=no"))
    name = top.name

    def attention(why: str) -> list[str]:
        return [f"EpicSpine attention: repo {name} ({branch}) needs the user: {why}. Tell the user exactly this; "
                "do not merge, rebase or push it yourself."]

    if ahead == 0:
        if dirty:
            return attention(f"{behind} commit(s) behind origin/{branch} and the working tree has uncommitted changes") if mine else []
        done = run("merge", "--ff-only", "--quiet", f"origin/{branch}", seconds=6) is not None
        return [f"EpicSpine sync: repo {name} {branch} fast-forwarded {behind} commit(s)"] if done else []
    if not mine:
        return []
    if behind:
        return attention(f"{branch} diverged from origin/{branch} ({ahead} ahead, {behind} behind)")
    if (field(text, "Integration policy") or "").lower() == "pr-approval":
        return attention(f"{ahead} unpushed commit(s) on {branch} but Integration policy is pr-approval")
    pushed = git(["push", "--quiet", "origin", branch], top, clock, 8)
    if pushed is not None and pushed.returncode == 0:
        return [f"EpicSpine sync: repo {name} pushed {ahead} commit(s) to origin/{branch}"]
    return attention(f"{ahead} unpushed commit(s) on {branch} and the push failed")


def run(cwd: Path, clock: Clock) -> list[str]:
    notes: list[str] = []
    top = out(git(["rev-parse", "--show-toplevel"], cwd, clock, 3))
    if not top:
        return notes
    for step in (sync, install):
        with contextlib.suppress(Exception):
            notes += step(Path(top), clock)
    return notes
