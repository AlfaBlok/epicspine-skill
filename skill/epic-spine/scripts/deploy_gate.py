#!/usr/bin/env python3
"""Deploy-gate and PR/CI-policy checks for ``auto_return`` (pure functions, no git, no network). When in doubt: no merge.

A repo may declare ``Deploy gate: <paths/globs>`` (AGENTS.md block and/or root spine): a push to main touching those paths rolls
a production deployment, so they go through PR/CI, never the background auto-merge. ``repo_sync.field`` reads only the first
token of a value, so the whole line is read here, from every occurrence in the text.

- ``Deploy gate:`` entries (split on commas, semicolons, spaces) must each be a repo-relative path prefix or glob (``*``, ``?``,
  ``**``); an entry without ``/`` matches that name at any depth. Anything else (a bare word such as a branch name, prose, a
  URL, ``..``, an absolute path, braces) makes the gate unparseable: auto-merge is blocked for the whole repo. ``none``/``n/a``/
  ``-`` or an empty value declare no gate. Matching is case-insensitive (more blocking, never less).
- An ``Integration policy:`` that mentions a PR or CI (``main-direct via self-merged CI-gated PR``) blocks auto-merge entirely.
- ``attention(top)`` (SessionStart, via ``repo_sync.run``; reads AGENTS.md, the root spine and ``.github/workflows``, no git, no
  network): a repo whose policy routes the whole repo through PR/CI (mentions a PR/CI, or is not ``main-direct``) without a
  ``Deploy gate:`` gets one ``EpicSpine attention:`` line: docs and spine edits (console-written answers too) get stranded.
  ``python3 deploy_gate.py --repo <path>`` prints it.
"""

from __future__ import annotations

import argparse
import re
from functools import lru_cache
from pathlib import Path

LINE = r"^[ \t>*_-]*{}[*_ ]*:[*_ \t`]*(.*)$"
NONE = {"", "none", "n/a", "na", "-", "no", "no gate"}
PATHISH = re.compile(r"^[A-Za-z0-9._@+~/*?-]+$")
PR_CI = re.compile(r"(?<![a-z])(prs?|pull[ -]requests?|ci)(?![a-z])", re.IGNORECASE)


def values(text: str, name: str) -> list[str]:
    """The rest of every ``name:`` line (markdown/backtick noise stripped), in document order."""
    found = re.findall(LINE.format(re.escape(name)), text, re.MULTILINE | re.IGNORECASE)
    return [v.replace("`", " ").strip() for v in found]


def entry_ok(entry: str) -> bool:
    if not PATHISH.match(entry) or entry.startswith(("/", "~", "origin/", "refs/")) or ".." in entry.split("/"):
        return False
    return "/" in entry or any(c in entry for c in "*?") or bool(re.search(r"\w\.\w+$", entry)) or entry.startswith(".")


def gate(text: str) -> tuple[list[str], str | None]:
    """(entries, problem): the declared gate entries, or a problem text when the value cannot be read confidently."""
    entries: list[str] = []
    for value in values(text, "Deploy gate"):
        if value.lower().strip(" .") in NONE:
            continue
        for raw in re.split(r"[,;\s]+", value):
            entry = raw.strip().removeprefix("./").rstrip(".,")
            if not entry:
                continue
            if not entry_ok(entry):
                return [], f"the Deploy gate value ({value[:60]!r}) is not only paths or globs (at {entry[:30]!r})"
            entries.append(entry)
    return entries, None


def policy_problem(text: str) -> str | None:
    """A reason when an ``Integration policy:`` line mentions a PR or CI (the repo merges through PR/CI, not by auto-merge)."""
    for value in values(text, "Integration policy"):
        if PR_CI.search(value):
            return f"its Integration policy mentions a PR/CI gate ({value[:60]!r})"
    return None


@lru_cache(maxsize=256)
def pattern(entry: str) -> re.Pattern[str]:
    out, i, e = [], 0, entry.lower()
    while i < len(e):
        if e.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif e.startswith("**", i):
            out.append(".*")
            i += 2
        else:
            out.append("[^/]*" if e[i] == "*" else "[^/]" if e[i] == "?" else re.escape(e[i]))
            i += 1
    return re.compile("".join(out))


def hit(entry: str, path: str) -> bool:
    """Whether ``path`` is under, or matches, ``entry`` (a directory entry covers everything below it)."""
    parts = path.lower().split("/")
    if "/" not in entry:
        return any(pattern(entry).fullmatch(p) for p in parts)
    anchored = pattern(entry.rstrip("/"))
    return any(anchored.fullmatch("/".join(parts[: i + 1])) for i in range(len(parts)))


def touched(entries: list[str], paths: list[str]) -> str | None:
    """The first gate entry that any of ``paths`` touches."""
    return next((e for e in entries if any(hit(e, p) for p in paths)), None)


DEPLOYISH = re.compile(r"deploy|publish|release|prod", re.IGNORECASE)
FIX = "declare Deploy gate: <paths that roll prod>, keep docs/spines main-direct, add paths-ignore for docs to the deploy workflow"


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def whole_repo(text: str) -> str | None:
    """The policy value when it routes the whole repo through PR/CI with no ``Deploy gate:`` entries, else None (an unreadable
    gate counts as declared: ``auto_return`` reports it)."""
    policies, (entries, problem) = values(text, "Integration policy"), gate(text)
    if not policies or entries or problem:
        return None
    return next((v for v in policies if PR_CI.search(v) or not v.lower().startswith("main-direct")), None)


def push_workflows(top: Path) -> list[str]:
    """Deploy-looking workflows that run on every push (a ``push`` trigger, no ``paths``/``paths-ignore`` filter)."""
    found = []
    for path in sorted((top / ".github" / "workflows").glob("*.y*ml"))[:50]:
        text = read(path)
        if DEPLOYISH.search(path.name + text[:300]) and re.search(r"^\s*push\s*:|on:\s*\[?[^\n]*\bpush\b", text, re.MULTILINE) \
                and not re.search(r"^\s*paths(-ignore)?\s*:", text, re.MULTILINE):
            found.append(path.relative_to(top).as_posix())
    return found


def attention(top: Path) -> list[str]:
    """SessionStart: one line when the repo's Integration policy gates the whole repo through PR/CI without a Deploy gate."""
    agents = read(top / "AGENTS.md")
    root = (values(agents, "Root spine") or [""])[0].split(" ")[0].rstrip(".")
    text = agents + "\n" + (read(top / root) if root and root != "none" and not root.startswith(("/", "..")) else "")
    policy = whole_repo(text)
    if policy is None:
        return []
    flows = push_workflows(top)
    every = f"; {', '.join(flows[:3])} run(s) on every push to main" if flows else ""
    quoted = " ".join(policy.split()).replace("( ", "(")
    quoted = quoted if len(quoted) <= 60 else quoted[:60].rsplit(" ", 1)[0] + "…"
    return [f"EpicSpine attention: {top.name}: Integration policy \"{quoted}\" gates the whole repo through PR/CI (no Deploy gate "
            f"declared), so docs/spine edits and console-written answers get stranded{every} — {FIX} (references/git-doctrine.md)"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the whole-repo PR/CI policy attention line for a repo (empty: fine).")
    parser.add_argument("--repo", type=Path, default=Path("."))
    lines = attention(parser.parse_args(argv).repo.resolve())
    print("\n".join(lines) if lines else "ok: no whole-repo PR/CI policy without a Deploy gate")
    return 1 if lines else 0


if __name__ == "__main__":
    raise SystemExit(main())
