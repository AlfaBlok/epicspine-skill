#!/usr/bin/env python3
"""Commit-msg hook (installed next to the pre-commit gate by ``agents_block.install_hook``): every commit names its
ticket. A message that names no row, ask, epic or learning code (``E62-S2``, ``M2-41``, ``EPIC-63``, ``E48-A1``,
``L-46``) and no spine path (``docs/spines/….md``) gets one warning line; the commit always goes through (exit 0).
Merges, reverts, fixups and the agent_team console's own writes (``via console``, desk chat, voice note) are exempt.
The agent_team console lists such commits that reached main for the Delivery Manager (agent_team E63-S7, same patterns:
console/server/src/status/orphanCommits.ts). ``python3 commit_msg.py --check "<message>"`` prints ok / orphan."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

TICKET_CODE = re.compile(r"(?<![A-Za-z0-9-])(?:EPIC-\d+(?:-[A-Z]{0,3}\d+[a-z]?)*|[A-Z]{1,4}-(?:\d+|[A-Z]{1,3}\d+[a-z]?)|[A-Z]{1,4}\d+[a-z]?(?:-[A-Z]{0,3}\d+[a-z]?)*)(?![A-Za-z0-9])")
SPINE_PATH = re.compile(r"\bdocs/(?:spines|tickets)/[\w./-]+\.md\b|(?<![\w./-])(?:[\w.-]+/)*[\w.-]*(?:EPIC|Epic|epic|SPINE|Spine|spine)[\w.-]*\.md\b")
EXEMPT_SUBJECT = re.compile(r"^(?:Merge\b|Revert\b|fixup! |squash! |amend! |epicspine[: ])", re.I)
EXEMPT_MESSAGE = re.compile(r"\bvia console\b|\((?:console|desk chat)\)|\(Jordi, (?:asking the Team desk|his voice note|desk chat)\)", re.I)
TRAILER = re.compile(r"^(?:Run|Ready|Co-Authored-By|Signed-off-by|Reviewed-by|Change-Id):\s", re.I)
MARK = "# epicspine:commit-msg"
CHAINER_MARK = "leak-watch:hook"  # infra-vps leak-watch (agent_team E59-S14): core.hooksPath hooks that exec the common-dir hook


def names_ticket(message: str) -> bool:
    """True when the message names a ticket or is exempt."""
    message = message.split("# ------------------------ >8 ------------------------")[0]  # `commit -v`: drop the diff
    text = "\n".join(l for l in message.splitlines() if not l.startswith("#")).strip()
    if not text:
        return True  # git aborts an empty message itself
    if EXEMPT_SUBJECT.search(text.splitlines()[0]) or EXEMPT_MESSAGE.search(text):
        return True
    body = re.sub(r"https?://\S+", "", "\n".join(l for l in text.splitlines() if not TRAILER.match(l)))
    return bool(TICKET_CODE.search(body) or SPINE_PATH.search(body))


def warning() -> str:
    return ("epicspine: this commit names no ticket (a row code such as E62-S2, or a spine path); "
            "amend it (git commit --amend) or the Delivery Manager has to find its row later")


def hook_text(skills: str) -> str:
    return (f"#!/bin/sh\n{MARK} (managed by agents_block.py; warns when a commit names no ticket; never blocks)\n"
            f'for s in {skills}; do\n  [ -f "$s/scripts/commit_msg.py" ] && exec python3 "$s/scripts/commit_msg.py" "$@"\ndone\nexit 0\n')


def hook_file(repo: Path, name: str) -> Path | None:
    """Where the repo's ``name`` hook goes (honors core.hooksPath); None outside a git repo. A core.hooksPath hook
    that is a leak-watch chainer runs ``$(git rev-parse --git-common-dir)/hooks/<name>``, so ours goes there, beside
    it (agent_team E63-S10); any other hook there stays foreign."""
    def git(*args: str) -> str:
        done = subprocess.run(["git", "-C", str(repo), "rev-parse", *args], capture_output=True, text=True)
        return done.stdout.strip() if done.returncode == 0 else ""
    path = git("--git-path", f"hooks/{name}")
    if not path:
        return None
    hook = repo / path
    if hook.is_file() and CHAINER_MARK in hook.read_text(encoding="utf-8", errors="replace"):
        common = git("--git-common-dir")
        chained = repo / common / "hooks" / name if common else None
        if chained and chained.resolve() != hook.resolve():
            return chained
    return hook


def install(repo: Path, skills: str) -> None:
    """Write the repo's commit-msg hook (honors core.hooksPath and leak-watch chainers); never replaces a foreign hook."""
    hook = hook_file(repo, "commit-msg")
    if hook is None:
        return
    old = hook.read_text(encoding="utf-8", errors="replace") if hook.is_file() else None
    if old is not None and MARK not in old:
        print(f"commit-msg: foreign hook at {hook}; EpicSpine ticket check not installed")
    elif old != hook_text(skills):
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(hook_text(skills), encoding="utf-8")
        hook.chmod(0o755)


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "--check":
        print("ok" if names_ticket(argv[1]) else "orphan")
        return 0
    try:
        message = Path(argv[0]).read_text(encoding="utf-8", errors="replace") if argv else ""
    except OSError:
        return 0
    if not names_ticket(message):
        print(warning(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
