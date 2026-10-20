# Ticket 2026-10-20: every agent pulls main at session start and before each task, and drift is surfaced

Status: proposed (doctrine owner decides; from infra-vps VH-T21, Jordi approved the work 2026-10-20)
Owner: epicspine-skill Delivery manager
Evidence: infra-vps `tickets/VH-T21-vps1-repo-sync-discipline.md` ("Findings 2026-10-20"), probed on vps1 (`t3agent`) 2026-10-20
Spine: [EPIC-0-OPERATING-SYSTEM](../EPIC-0-OPERATING-SYSTEM.md) (suggested child: EPIC-4 Doctrine 2)

## Rule proposed

Every agent, local or remote, runs a fetch of the repo's integration branch at session start and again before starting each task (ticket, worktree, branch). Behind or diverged state is shown in the reply, never silently left. Before any branch or worktree is cut, it is cut from fresh `origin/<integration branch>`.

## What already exists

- SessionStart hook: updates the skill and fast-forwards the repo the agent opened (`repo_sync.sync`, clean + only behind).
- 15-minute background job (`background_sync.py`): fast-forwards the integration branch of every repo it finds with a root spine, pushes ahead, flags idle branches and worktrees (`mess`).
- Both installed and working on vps1 for `t3agent`: cron entry, SessionStart/Stop hooks in `.claude`, `.claude_seat1`, `.claude_seat2` and `.codex`.

## Gap (measured on vps1, 2026-10-20)

1. **Worktrees branch from stale main.** The sync only touches the checked-out integration branch. poly-maker main is current, yet `poly-maker-wt-m7-deploy` and `-one-logger` were cut 761 commits behind origin/main, `-m7-t4b` 518, `-polkadot-frog` and `-whale` 74. Nothing fetches or checks base freshness when a worktree is created.
2. **No fetch before a task.** The hook runs once per session, up to 15 min stale; a long session (or a manager dispatching several workers over hours) starts each task on whatever was last pulled.
3. **Drift is only reported for the integration branch.** Worktree branches that are behind, repos without a root spine (`nectary`, `zenod_memory`, `zenod-cloud` not in the sync status file) and repos outside the scanned root (`/root/github/*`, 1000-1500 commits behind, dirty) show no `behind` line anywhere.
4. **Dirty + behind is silent unless on the integration branch.** `repo_sync` returns `[]` for non-integration branches, so a stale feature branch never raises attention.
5. **The fetch itself can hurt.** A fetch under a short timeout left orphaned `tmp_pack` files and filled a disk (VH-T20); fixed by `fetch_guard.py` (9c2da17). Any "fetch before each task" must go through `fetch_guard`, never raw `git fetch` with a short kill.

## Acceptance

- [ ] AC-1 Add to the global block (and the role protocols): fetch via the fetch guard at session start and before each task; state `behind N` or `diverged` in the reply when non-zero.
- [ ] AC-2 Worktree creation helper (or rule): `git worktree add -b wt/<task> <path> origin/<integration branch>` after a guarded fetch; SessionStart/background `mess` flags worktrees whose merge-base with origin/main is more than N commits behind.
- [ ] AC-3 `repo_sync` / `repo_state` report behind/diverged for every checked-out branch of every worktree (read-only; no merge), not only the integration branch.
- [ ] AC-4 Background job scans every git repo under the user's repo root(s), not only those with a root spine; a `ROOTS` setting for `/root/github`-style paths.
- [ ] AC-5 Tests: stale worktree is flagged; a no-spine repo is fast-forwarded when clean; a diverged repo yields an attention line and is never touched.

## Not proposed

No auto-rebase, reset, stash or checkout of dirty, diverged or non-default branches; fast-forward of clean default branches only (current behavior).
