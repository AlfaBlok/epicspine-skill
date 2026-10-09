# Repo Hygiene And Sweeps

A **sweep** is a cheap standard WORKER task that reclaims disk from finished git worktrees and local branches. It is not a role and not part of integration. The delivery manager owns the schedule and the record; the user only talks to the manager.

Normal-path hygiene is not a sweep: after integrating a worker, the manager removes its worktree and local branch (`git worktree remove`, `git branch -d`, `git worktree prune`). A sweep is the backstop for what slipped through.

## When To Dispatch A Sweep

The manager checks at bind and at end of each task. Dispatch when any trigger holds:

- `Last sweep` is absent or older than 7 days.
- More than one worktree, or more than one local branch besides `main`.
- Sibling `wt-*` directories exceed 500 MB total.
- The user asks.

Never sweep while integrating; pass the sweep the list of ACTIVE worktrees to skip.

```sh
git worktree list
git branch --list
du -sk ../wt-* 2>/dev/null
```

## Sweep Classification

Classify every worktree and local branch, then act only on what is safe:

| State | Test | Action |
|---|---|---|
| Merged | `git merge-base --is-ancestor <branch> main` exits 0 | eligible to remove |
| Clean | `git status --porcelain` in the worktree is empty | required with merged |
| Dirty, unmerged, or active | either test fails, or the worktree is ACTIVE | keep and report; never delete or force |
| Remote branch | merged and name starts with `wt/` | delete it; report every other remote |
| Orphan `wt-*` directory | not registered with git | report path and size; delete only if empty |
| Primary checkout | always | report only; never clean |

Remove in this order: `git worktree remove <path>`, then `git branch -d <branch>`, then `git worktree prune` and `git fetch --prune`. Never rewrite history, force-push, use `git branch -D`, or touch `main`.

## Record And Report

Write one line to the root spine: `Last sweep: YYYY-MM-DD, <result in ≤ 10 words>` (absent means never). A sweep returns one summary line (date, N worktrees + M branches removed, MB reclaimed from `du -sk` before/after) plus the kept / needs-decision list with reasons.

Tell the user only when something needs their decision or more than 100 MB was reclaimed; otherwise the record line is enough.
