#!/usr/bin/env python3
"""Manager-guard rules for git and gh: each takes (args, heredoc body, Ctx) and
returns a deny reason or None. git: reads, fetch, the integrate sequence (rebase inside a linked worktree,
merge/pull --ff-only, non-force push, revert, worktree add/remove, branch -d,
checkout main) and add/commit of manager-editable files only. gh: views, lists,
GET api calls and issue tracking. Stdlib only, Python 3.10+.
"""

from __future__ import annotations

import os
import re
import subprocess

from guard_policy import Ctx, path_ok, resolve

GIT_READ = set("""status log diff show fetch rev-parse rev-list ls-files ls-tree ls-remote cat-file blame
describe shortlog grep show-ref merge-base for-each-ref name-rev count-objects check-ignore var help version
whatchanged range-diff cherry diff-tree diff-index diff-files annotate show-branch verify-commit""".split())
GIT_VALUE = {"-m", "-F", "-C", "-c", "-t", "--author", "--date", "--fixup", "--squash", "--cleanup", "--trailer"}
LIST_FLAGS = {"-a", "-r", "-v", "-vv", "--all", "--list", "-l", "--contains", "--merged", "--no-merged", "--show-current"}
INTEGRATION = ("main", "master", "-")


def git_out(cwd: str, *args: str) -> list[str]:
    proc = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=10)
    return [ln for ln in proc.stdout.splitlines() if ln.strip()] if proc.returncode == 0 else []


def linked_worktree(path: str) -> bool:
    """True when ``path`` is inside a linked git worktree (not the main checkout)."""
    out = git_out(path, "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir")
    return len(out) == 2 and os.path.realpath(out[0]) != os.path.realpath(out[1])


def _files_ok(cwd: str, rels: list[str], ctx: Ctx) -> str | None:
    top = (git_out(cwd, "rev-parse", "--show-toplevel") or [cwd])[0]
    bad = [r for r in rels if not path_ok(os.path.join(top, r), ctx)]
    return f"it commits files the manager may not edit: {', '.join(bad[:4])}" if bad else None


def git(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    cwd, i = ctx.cwd, 0
    while i < len(args) and args[i].startswith("-"):
        i += 1
        if args[i - 1] == "-C" and i < len(args):
            cwd = resolve(ctx.cwd, args[i])
        if args[i - 1] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace"):
            i += 1
    if i >= len(args) or args[i] in GIT_READ:
        return None
    sub, rest = args[i], args[i + 1:]
    flags = {a for a in rest if a.startswith("-")}
    pos, k = [], 0
    while k < len(rest):
        if rest[k] in GIT_VALUE or re.fullmatch(r"-[a-zA-Z]+[mFCct]", rest[k]):
            k += 1
        elif not rest[k].startswith("-"):
            pos.append(rest[k])
        k += 1
    head = pos[0] if pos else ""
    ok = {
        "branch": not flags & {"-D", "-f", "--force", "-m", "-M", "-c", "-C", "--copy", "--move", "-u",
                               "--set-upstream-to", "--unset-upstream", "--edit-description"}
                  and (not pos or bool(flags & ({"-d", "--delete"} | LIST_FLAGS))),
        "remote": head in ("", "show", "get-url"),
        "config": not any(f.startswith(("--unset", "--add", "--replace", "--rename", "--remove", "--edit"))
                          for f in flags) and "-e" not in flags and len(pos) <= 1,
        "stash": head in ("list", "show"),
        "tag": not pos or bool(flags & {"-l", "--list"}),
        "reflog": head in ("", "show"),
    }
    if sub in ok:
        return None if ok[sub] else f"`git {sub} {' '.join(rest)}` changes state"
    if ctx.remote:
        return f"`git {sub}` is not read-only"
    if sub in ("worktree", "merge", "pull", "revert", "checkout", "switch", "push", "rebase"):
        allowed = {
            "worktree": head in ("list", "prune", "add", "remove", "repair") and not (
                head == "remove" and flags & {"-f", "--force"}),
            "merge": bool(flags & {"--ff-only", "--abort"}),
            "pull": "--ff-only" in flags and not flags & {"--rebase", "-r"},
            "revert": True,
            "checkout": len(pos) == 1 and head in INTEGRATION and not flags - {"-q", "--quiet"},
            "push": not any(f.startswith(("--force", "--delete", "--mirror", "--prune")) or f in ("-f", "-d")
                            for f in flags) and not any(p.startswith(("+", ":")) for p in pos),
            "rebase": bool(flags & {"--abort", "--continue", "--skip", "--quit"}) or (
                linked_worktree(cwd) and not flags & {"-i", "--interactive", "--onto", "--root", "-x", "--exec"}),
        }
        allowed["switch"] = allowed["checkout"]
        if allowed[sub]:
            return None
        hint = " (rebase only inside the worker's worktree: git -C <worktree> rebase main)" if sub == "rebase" else ""
        return f"`git {sub} {' '.join(rest)}` is not an integrate step{hint}"
    if sub == "add":
        if flags & {"-p", "--patch", "-i", "--interactive", "-f", "--force"}:
            return "`git add` with -p/-i/-f is worker work"
        if flags & {"-A", "--all", "-u", "--update"} or any(p in (".", "*") or "*" in p for p in pos):
            top = (git_out(cwd, "rev-parse", "--show-toplevel") or [cwd])[0]
            files = [os.path.join(top, ln[3:].split(" -> ")[-1]) for ln in
                     git_out(cwd, "status", "--porcelain", "--untracked-files=all")]
        else:
            files = [resolve(cwd, p) for p in pos if p != "--"]
        ctx.adds.update(files)
        bad = [f for f in files if not path_ok(f, ctx)]
        return f"it stages files the manager may not edit: {', '.join(bad[:4])}" if bad else None
    if sub == "commit":
        rels = git_out(cwd, "diff", "--cached", "--name-only")
        if any(f == "--all" or re.match(r"^-[a-zA-Z]*a", f) for f in flags):
            rels += git_out(cwd, "diff", "--name-only")
        if "--amend" in flags:
            rels += git_out(cwd, "show", "--name-only", "--format=", "HEAD")
        top = (git_out(cwd, "rev-parse", "--show-toplevel") or [cwd])[0]
        rels += [os.path.relpath(p, top) for p in ctx.adds] + [os.path.relpath(resolve(cwd, p), top) for p in pos]
        return _files_ok(cwd, sorted(set(rels)), ctx)
    return f"`git {sub}` is worker work"


GH_GROUPS = set("""pr issue repo run release workflow label gist cache secret variable ruleset search auth api
status browse extension alias codespace project org""".split())
GH_READ = {"view", "list", "status", "diff", "checks", "watch"}
GH_TICKET = {"issue": {"create", "comment", "edit", "close", "reopen"}, "pr": {"comment"}}


def gh(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    pos = [a for a in args if not a.startswith("-")]
    grps = [p for p in pos if p in GH_GROUPS]
    if not grps:
        return None if not pos else f"`gh {pos[0]}` is not on the manager allowlist"
    grp = grps[0]
    after = pos[pos.index(grp) + 1:]
    act = after[0] if after else ""
    if grp in ("search", "status", "browse") or (grp == "auth" and act in ("status", "token")) or act in GH_READ:
        return None
    if grp == "api":
        joined = " ".join(args)
        method = (re.search(r"(?:-X|--method)[= ]?(\w+)", joined) or [None, None])[1]
        fields = re.search(r"(?:^| )(-f|-F|--field|--raw-field|--input)\b", joined)
        if (act == "graphql" and "mutation" not in joined) or (method or "GET").upper() in ("GET", "HEAD") and (
                not fields or method):
            return None
        return "`gh api` with a write method or fields is worker work"
    if not ctx.remote and act in GH_TICKET.get(grp, ()):
        return None
    return f"`gh {grp} {act}` changes state; dispatch a worker"
