# Tickets of the root spine: detail

Page of [EPIC-0](../EPIC-0-OPERATING-SYSTEM.md). The Issue Ledger there keeps one line per ticket; the full text of every cell over 200 characters, as it stood in the ledger, is here. Tickets are numbered by row position in the ledger (rows whose cells all fit stay in the ledger only).

## Ticket 9

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker E (Sonnet 5.5 subagent)
- **Title:** Vanilla dispatch default: shipped skill drops the author's hardwired profile; default becomes a lower-cost harness-native subagent; ask once when unset and record the answer as the root spine `Dispatch profile:`; AGENTS.md block defers to it
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** wt/dispatch-defaults
- **Base:** 940d9f8
- **Latest Evidence:** integrated (ff-only, c3d2dc3); 138 tests + strict validate + agents_block + manifest green; roles-and-dispatch budget 100->105; worktree removed
- **Last Verified:** 2026-10-10
- **Next Action:** done

## Ticket 10

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker F (Sonnet 5.5 subagent)
- **Title:** Make skill updates actually work: content-tree freshness (not head commit), resolve harness symlinks to the hub, cache the last result not 'fresh', 1-day window, PR per user
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** PR #27
- **Base:** 974021d
- **Latest Evidence:** merged ff (97b7535); 145 tests + CI + agents_block + manifest green; hub bootstrapped via real path, then upgrade + status --force via ~/.claude symlink = fresh; docs-only commit stays fresh; worktree removed
- **Last Verified:** 2026-10-10
- **Next Action:** done

## Ticket 11

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker G (Sonnet 5.5 subagent)
- **Title:** Always-on bind on every major harness: harness-neutral global block + `install-global` (instruction files + session hooks on by default; unsupported reported), repo pointers (CLAUDE.md/GEMINI.md -> AGENTS.md), first-message route
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** wt/always-on-all-harnesses
- **Base:** a272d1f
- **Latest Evidence:** integrated (ff-only, 5088c2f); 160 tests + block + validate + manifest green; install-global run here; cold "hi" pass on Claude Code, Codex, OpenCode; Gemini untested (no API key); worktree removed
- **Last Verified:** 2026-10-10
- **Next Action:** Gemini cold start

## Ticket 15

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Machine dispatcher: env `EPICSPINE_DISPATCHER` (status/pick/done JSON, via t3_delegate_task) routes workers on any host; repo opt-out `Dispatch profile: local-only`; `install-global --config-dir` links the skill per Claude config dir
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** PR #30 (merged); PR #29 guard allowance parked with #28
- **Base:** adbc1ce
- **Latest Evidence:** 200 tests + CI green; agent_team rollout done (4026755, 7dea50c), block 2026.10.13.2 live on vps1
- **Last Verified:** 2026-10-13
- **Next Action:** done

## Ticket 16

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Dispatch suffix always: block line forces env check + `status` on every first turn (greetings included), suffix `· dispatch: <status.name> (<available>/<capacity> seats)` verbatim, rule 1 pointer; skill 2026.10.14.1
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** fix/dispatch-suffix-always
- **Base:** be4c1d1
- **Latest Evidence:** tests + strict validate + manifest green; vps1 reinstall done, bare-"hi" retest pass on seat1/seat2
- **Last Verified:** 2026-10-14
- **Next Action:** done

## Ticket 22

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Session autosync: SessionStart syncs skill + canonical dispatch profile + current repo and self-installs the AGENTS.md block / Operating Learnings; learnings saved immediately; url_gate fires only for HTML touched this turn; skill 2026.10.16.4
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** feat/session-autosync
- **Base:** see branch
- **Latest Evidence:** tests green (328), manifest regenerated, dry-run install on 3 real repo copies clean; Mac needs one-time bootstrap line
- **Last Verified:** 2026-10-16
- **Next Action:** delivery manager integrates; user runs the Mac line once

## Ticket 23

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Sync every step: Stop-hook push after every turn (Claude + Codex), push/record rules in the global block, AGENTS.md block in every repo with an origin (`Root spine: none`), opt-out, Codex hooks + trust; skill 2026.10.16.5
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** feat/sync-every-step
- **Base:** see branch
- **Latest Evidence:** tests green (352), real-codex test green (EPICSPINE_TEST_CODEX=1), Codex SessionStart+Stop verified against a mock model, manifest regenerated
- **Last Verified:** 2026-10-16
- **Next Action:** delivery manager integrates, then re-runs install-global on every config dir (VPS and Mac)

## Ticket 24

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Re-hook after update: SessionStart re-runs install-global (Claude + Codex, subprocess of the new code, throttled when only stale) so a self-updated machine registers new hooks like the Stop push; `install-global --only`; skill 2026.10.16.6
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** fix/rehook-after-update
- **Base:** see branch
- **Latest Evidence:** tests green (364), manifest regenerated
- **Last Verified:** 2026-10-16
- **Next Action:** draft

## Ticket 25

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Multi-machine commit-often: the always-on block (rule 6 + Sync line), session-sync.md and SKILL.md explain that agents on a VPS and a laptop share repos via GitHub and see only committed+pushed work, so commit each passing step at once; skill 2026.10.16.7
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** feat/multi-machine-commit-often
- **Base:** DONE: merged bf3b834, pushed
- **Latest Evidence:** tests green (364), manifest regenerated
- **Last Verified:** 2026-10-16
- **Next Action:** done

## Ticket 26

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Stale repo rules: a learning that reverses a rule sweeps the repo for current instructions still saying the old thing (global block rule 7, SKILL.md rule 5, learnings.md); SessionStart flags old vendored copies of the epic-spine skill (`vendored_skill.py`); skill 2026.10.16.8
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** feat/stale-repo-rules
- **Base:** see branch
- **Latest Evidence:** tests green (373), manifest regenerated
- **Last Verified:** 2026-10-16
- **Next Action:** delivery manager integrates

## Ticket 27

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Opus 5.5, native)
- **Title:** Background sync: machine-wide cron/launchd job syncs every repo under the repo roots (ff-pull, push per policy, pre-commit gate, vendored-copy check), writes `~/.agents/epicspine-sync-status.json`; SessionStart prints attention for any repo; scheduled by install-global and rehook, removed by uninstall-global; skill 2026.10.16.9
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** feat/background-sync
- **Base:** ad29302
- **Latest Evidence:** 421 tests green, manifest regenerated, real crontab untouched by tests
- **Last Verified:** 2026-10-16
- **Next Action:** merge per Integration policy; run install-global on the VPS and the Mac

## Ticket 28

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** No local mess: background job backup-pushes local-only branches (never forced; opt-outs `EPICSPINE_PUSH_BRANCHES=off` / `Push branches: off`) and reports idle/merged worktrees, old uncommitted changes and stale local servers (`local_mess.py`, `local_servers.py`); rules: stop servers + remove worktree after integrating, push-and-report an unintegrated worker branch
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** feat/no-local-mess
- **Base:** main
- **Latest Evidence:** tests green, manifest regenerated, release 2026.10.16.10
- **Last Verified:** 2026-10-16
- **Next Action:** none

## Ticket 29

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Return to main: additive no-risk work straight to main, `Ready: yes` marker, no branch outlives its task, soft 3 d/14 d escalation, cleanup safety checklist; `auto_return.py` auto-merges Ready additive branches in main-direct repos and deletes merged ones, `repo_state.py` state line + worktree cap + repo table, vendored-copy 7-day tolerance; cleanup report `docs/hygiene/2026-10-16-cleanup.md`; skill 2026.10.16.11
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** feat/return-to-main
- **Base:** main
- **Latest Evidence:** 478 tests green, manifest regenerated, release 2026.10.16.11
- **Last Verified:** 2026-10-16
- **Next Action:** none

## Ticket 30

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Deploy exception: `main-direct` default for every repo; PR/CI only for a declared `Deploy gate:` (paths/workflows/branches whose push to main rolls a complex production deployment, e.g. zenod), never the whole repo; global block 2/5, SKILL.md 4, git-doctrine, templates, L-12; skill 2026.10.16.12 (auto_return gap closed in the .13 row)
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** feat/deploy-exception
- **Base:** main
- **Latest Evidence:** tests green, manifest regenerated, release 2026.10.16.12
- **Last Verified:** 2026-10-16
- **Next Action:** none

## Ticket 31

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Deploy gate in auto-merge: `auto_return.py` blocks branches touching a `Deploy gate:` path/glob, blocks the repo when the gate is unparseable or the Integration policy mentions PR/CI (`scripts/deploy_gate.py`, `tests/test_deploy_gate.py`); git-doctrine, session-sync; skill 2026.10.16.13
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** fix/automerge-deploy-gate
- **Base:** main
- **Latest Evidence:** tests green, manifest regenerated, release 2026.10.16.13
- **Last Verified:** 2026-10-16
- **Next Action:** none

## Ticket 32

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** Fetch guard (infra-vps VH-T20 incident: vps1 disk filled by orphan `tmp_pack_*` from the 15 s background fetch timeout): timeouts kill git's process group, clean only this run's tmp packs, back off after 2 strikes (30 min doubling to 6 h) with an attention line; also guards auto_return's fetches; `scripts/fetch_guard.py`, `tests/test_background_sync.py` FetchTimeoutTest; skill 2026.10.20.1
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** wt/fetch-timeout-tmp-pack
- **Base:** f63cf51
- **Latest Evidence:** new tests green; full suite differs from the pre-change baseline only by them (20 env failures pre-exist in this worktree); manifest regenerated
- **Last Verified:** 2026-10-20
- **Next Action:** manager merges

## Ticket 33

- **Issue:** draft
- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5, native)
- **Title:** EPIC-4 steps 10+11: `## Outcome` before close (doctrine, `--trackable` rule for done/superseded spines, `spines.py --json` `outcome`, EPIC-1/2 backfilled) and `current_state` JSON + manager updates Current State every session/wake; `tests/test_outcome.py`; skill 2026.10.20.2
- **Status:** draft
- **Depends On:** none
- **PR/Branch:** wt/outcome
- **Base:** see branch
- **Latest Evidence:** new tests green; manifest regenerated
- **Last Verified:** 2026-10-20
- **Next Action:** manager merges
