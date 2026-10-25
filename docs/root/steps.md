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

## Done ledger

Rows moved from the [EPIC-0](../EPIC-0-OPERATING-SYSTEM.md) Issue Ledger once their Next Action was done/none, unchanged apart from detail links made local.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | /root delivery manager | Always-on AGENTS.md block + installer + CI check | draft | none | wt/agents-block | 1993233 | integrated on 02d7a88; 115 tests + block + manifest green; worktree removed | 2026-10-09 | done |
| draft | Ticket worker | /root/kernel (thread 441c3c64) | Lean SKILL.md kernel + Default Behaviors card + CI line budgets | draft | none | wt/kernel | main | integrated on d547410; 120 tests + agents_block check + strict validate + manifest green | 2026-10-09 | done |
| draft | Ticket worker | /root delivery manager | Centralize installed skill: hub + harness symlinks + pin SOURCE | draft | none | n/a | main | ~/.agents/skills/epic-spine real copy; Claude/OpenCode/Codex symlink to it; skill_update status fresh | 2026-10-09 | done |
| draft | Ticket worker | /root delivery manager | Cold-start test: fresh agent per provider binds and dispatches | draft | none | n/a | main | passed on opencode_2/deepseek-v4.1-flash: bound as delivery manager, named the default profile, card present, no dead ends | 2026-10-09 | done |
| draft | Ticket worker | worker A (default profile) | Default-behavior contract tests + SMOKE.md baseline | draft | none | wt/behavior-tests | b620d50 | integrated on 3108192; 125 tests green; mutation check fails as intended; smoke baseline P1 pass, P2 pass, P3 provisional pass (dry run stopped at first read; tighten preamble) | 2026-10-09 | done |
| draft | Ticket worker | worker B (default profile) | Adopt L-9..L-11 doctrine + extend tests/smoke | draft | worker A | wt/adopt-l9-l11 | 3108192 | integrated on a868281 (rebased over 7d617c2); 136 tests, strict validate, block check, manifest green; smoke 4/4 after P2 test rewrite (a694ae2) | 2026-10-09 | done |
| draft | Ticket worker | worker D (default profile) | Shortlist template: table-first compact layout (user feedback on demo page) | draft | worker C | wt/shortlist-table-first | a868281 | integrated (ff-only, 7781d8e); 137 tests + strict validate + agents_block + manifest green; screenshot reviewed; demo re-served 200; worktree removed; installed skill upgraded | 2026-10-09 | done |
| draft | Ticket worker | worker E (Sonnet 5.5 subagent) | Vanilla dispatch default: shipped skill uses a lower-cost native subagent; ask once, record `Dispatch profile:` [detail](#ticket-9) | draft | none | wt/dispatch-defaults | 940d9f8 | integrated (ff-only, c3d2dc3); 138 tests + strict validate + agents_block + manifest green; roles-and-dispatch budget 100->105; worktree removed | 2026-10-10 | done |
| draft | Ticket worker | worker F (Sonnet 5.5 subagent) | Make skill updates actually work: content-tree freshness (not head commit), resolve harness symlinks to the hub, cache the last result not 'fresh', 1-day window, PR per user | draft | none | PR #27 | 974021d | merged ff (97b7535); 145 tests + CI + block + manifest green; skill update status fresh; worktree removed [detail](#ticket-10) | 2026-10-10 | done |
| draft | Ticket worker | worker (Sonnet 5.5 subagent) | Machine-wide dispatch profile: one user-level file `~/.agents/epicspine-profile.md` used in every repo; repo `Dispatch profile:` only overrides; ask once and save at machine level | draft | none | wt/machine-profile | 3c12fbe | integrated (ff-only, ac3c4d4); 160 tests + agents_block + manifest green; machine file written; worktree removed | 2026-10-10 | done |
| draft | Ticket worker | worker (Sonnet 5.5 subagent) | Profile command + cold-start test: `profile` show/set command for `~/.agents/epicspine-profile.md`; docs point to it; tests prove ask-once, save, reuse across repos | draft | none | wt/profile-command | fcddfe5 | integrated (ff-only, 04c28e0); 165 tests + agents_block + manifest green; `profile` verified live (machine, rc 0) and empty home (unset, rc 3); worktree removed | 2026-10-10 | done |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Machine dispatcher: env `EPICSPINE_DISPATCHER` (status/pick/done JSON) routes workers on any host; opt-out `Dispatch profile: local-only` [detail](#ticket-15) | draft | none | PR #30 (merged); PR #29 guard allowance parked with #28 | adbc1ce | 200 tests + CI green; agent_team rollout done (4026755, 7dea50c), block 2026.10.13.2 live on vps1 | 2026-10-13 | done |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Dispatch suffix always: block forces the env check + `status` on every first turn; suffix `· dispatch: <name> (<available>/<capacity> seats)` [detail](#ticket-16) | draft | none | fix/dispatch-suffix-always | be4c1d1 | tests + strict validate + manifest green; vps1 reinstall done, bare-"hi" retest pass on seat1/seat2 | 2026-10-14 | done |
| draft | Ticket worker | worker (Sonnet 5.5, seat2 via seat pool) | Headless auto-detect: no display + Tailscale up gives tailnet links with no setup; env only overrides | draft | none | wt/auto-host (removed) | c97e1ff | integrated ff (4f4fe25) after r2 rebase; vps1 manual flag removed | 2026-10-14 | done |
| draft | Ticket worker | workers (Sonnet 5.5, seat pool) | Close-out: gate quote fix, self-healing global copy, install mirror scope, migrate 4 repo blocks + spine nits | draft | none | wt/selfheal, wt/install-scope (removed); zenod PRs #1405, #1406, #1407 (restored vendored-copy line) | dbe9d4f | integrated ff (77f4377, 066dc43); 240 tests x3 env green; 4 repos check rc 0 | 2026-10-14 | done |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Multi-machine commit-often: block rule 6 + Sync line, session-sync.md, SKILL.md: repos shared via GitHub; skill 2026.10.16.7 [detail](#ticket-25) | draft | none | feat/multi-machine-commit-often | DONE: merged bf3b834, pushed | tests green (364), manifest regenerated | 2026-10-16 | done |
| draft | Ticket worker | worker (Sonnet 5.5, native) | No local mess: background job backup-pushes local-only branches, reports idle worktrees, old changes, stale servers; skill 2026.10.16.10 [detail](#ticket-28) | draft | none | feat/no-local-mess | main | tests green, manifest regenerated, release 2026.10.16.10 | 2026-10-16 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Return to main: additive work straight to main, `Ready: yes`, no branch outlives its task, `auto_return.py`, `repo_state.py`; skill 2026.10.16.11 [detail](#ticket-29) | draft | none | feat/return-to-main | main | 478 tests green, manifest regenerated, release 2026.10.16.11 | 2026-10-16 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Deploy exception: `main-direct` default; PR/CI only for a declared `Deploy gate:` (e.g. zenod); block, SKILL.md, L-12; skill 2026.10.16.12 [detail](#ticket-30) | draft | none | feat/deploy-exception | main | tests green, manifest regenerated, release 2026.10.16.12 | 2026-10-16 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Deploy gate in auto-merge: `auto_return.py` blocks branches touching a `Deploy gate:` path or an unparseable gate; skill 2026.10.16.13 [detail](#ticket-31) | draft | none | fix/automerge-deploy-gate | main | tests green, manifest regenerated, release 2026.10.16.13 | 2026-10-16 | none |
| draft | Ticket worker | worker C (default profile) | Shortlist-by-default: JSON + generated sortable/filterable HTML as the default deliverable when a shortlist is key (port from abnb_agent SHORTLIST_STANDARD, check idea_scraper) | done | none (SKILL.md/MANIFEST merge serialized after B) | wt/shortlist-default | 5fffe5a | integrated (ff, 7d617c2; table-first follow-up 7781d8e) | 2026-10-09 | none |
| draft | Ticket worker | worker G (Sonnet 5.5 subagent) | Always-on bind on every major harness: neutral global block + `install-global` + repo pointers + first-message route [detail](root/steps.md#ticket-11) | done | none | wt/always-on-all-harnesses | a272d1f | integrated (ff-only, 5088c2f); 160 tests + block + validate + manifest green; install-global run here; cold "hi" pass on Claude Code, Codex, OpenCode; Gemini untested (no API key); worktree removed | 2026-10-10 | none |
| draft | Ticket worker | worker (Sonnet 5.5 subagent) | Enforce the served-URL rule on output: Stop hook `url_gate.py` + install-global wiring + rule line in both always-on blocks + handoff url/port/pid | done | none | wt/url-gate | main | integrated (ff-only, 2346d2d); 193 tests + strict validate + block check + manifest green; e2e block/allow proof; worktree removed | 2026-10-11 | none |
| draft | Ticket worker | worker (Sonnet 5.5, seat1 via seat pool) | Artifact host for remote readers: env `EPICSPINE_ARTIFACT_HOST` + `scripts/artifact_host.py`, url_gate host-aware, `install-global --artifact-host`, blocks + artifacts.md | done | none | wt/artifact-host (removed) | 31aaf28 | integrated ff (6c5498c); 215 tests + validate + block + manifest green; round 2 rebased over be4c1d1 (round 1 would have reverted it); flag set on vps1 (3 seats + systemd drop-in) | 2026-10-14 | none |
| draft | Ticket worker | worker (Sonnet 5.5, seat1 via seat pool) | Live shared rules: global block is the single source (hook-injected), thin repo block, pointer-only global files, self-migrating old repo blocks, supersede clause | done | none | wt/live-rules (removed) | 1856f92 | integrated ff (c97e1ff) after r2 (hermetic tests; old repo block cannot outrank live rules) | 2026-10-14 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Session autosync: SessionStart syncs skill, dispatch profile and repo; self-installs AGENTS.md block / Learnings; skill 2026.10.16.4 [detail](root/steps.md#ticket-22) | done | none | feat/session-autosync | see branch | merged to main (51a879b, release 2026.10.16.4); tests green (328), manifest regenerated, dry-run install on 3 real repo copies clean; Mac bootstrap now automatic via re-hook (358b0e5) | 2026-10-16 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Sync every step: Stop-hook push after every turn (Claude + Codex), AGENTS.md block in every repo with an origin; skill 2026.10.16.5 [detail](root/steps.md#ticket-23) | done | none | feat/sync-every-step | see branch | merged to main (0de3e04, release 2026.10.16.5); tests green (352), real-codex test green (EPICSPINE_TEST_CODEX=1), Codex SessionStart+Stop verified against a mock model, manifest regenerated | 2026-10-16 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Re-hook after update: SessionStart re-runs install-global so a self-updated machine registers new hooks; skill 2026.10.16.6 [detail](root/steps.md#ticket-24) | done | none | fix/rehook-after-update | see branch | merged to main (358b0e5, release 2026.10.16.6); tests green (364), manifest regenerated | 2026-10-16 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Stale repo rules: a reversing learning sweeps the repo for instructions saying the old thing; vendored skill copies flagged; skill 2026.10.16.8 [detail](root/steps.md#ticket-26) | done | none | feat/stale-repo-rules | see branch | merged to main (ad29302, release 2026.10.16.8); tests green (373), manifest regenerated | 2026-10-16 | none |
| draft | Ticket worker | worker (Opus 5.5, native) | Background sync: machine-wide cron/launchd job syncs every repo, writes `~/.agents/epicspine-sync-status.json`; skill 2026.10.16.9 [detail](root/steps.md#ticket-27) | done | none | feat/background-sync | ad29302 | merged to main (70bc9d4, release 2026.10.16.9); 421 tests green, manifest regenerated, real crontab untouched by tests | 2026-10-16 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Fetch guard (infra-vps VH-T20): fetch timeouts kill git's process group, clean own tmp packs, back off after 2 strikes; skill 2026.10.20.1 [detail](root/steps.md#ticket-32) | done | none | wt/fetch-timeout-tmp-pack | f63cf51 | merged to main (9c2da17, release 0891cbb, 2026.10.20.1); new tests green; full suite differs from the pre-change baseline only by them (20 env failures pre-exist in this worktree); manifest regenerated | 2026-10-20 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native) | EPIC-4 steps 10+11: `## Outcome` before close and `current_state` in `--json`; `tests/test_outcome.py`; skill 2026.10.20.2 [detail](root/steps.md#ticket-33) | done | none | wt/outcome | see branch | merged to main (21adcba, release 2026.10.20.2); new tests green; manifest regenerated | 2026-10-20 | none |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent) | ticket-34 Ask states & refs (agent_team L-12 duplicate cards): `superseded` state, done notes, `Waiting on:` codes as `waits_on[]` refs, advisories (D19 pt 4) | done | none | wt/ask-states-refs (removed) | 6be164a | merged e39fc79, 2026.10.23.1; 633 tests green; live JSON verified | 2026-10-23 | none |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent from agent_team EPIC-8 E8-S1) | ticket-35 Standing approvals: `[grant …]` lines, revoke/expiry, inheritance, `grants[]` in `--json`, advisories ([doctrine](doctrine/standing-approvals.md) v1) | done | none | wt/standing-approvals | 5bfaf22 | skill 2026.10.24.1; 643 tests green (10 new, tests/test_grants.py); live JSON on whatgpt_v3: EPIC-0 own E0-G1..G10, EPIC-1 inherits all 10 | 2026-10-24 | none |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent from agent_team EPIC-8 E8-S4) | ticket-36 Ask writing (agent_team L-13/L-14): blocking step only, decision first, one per ask; 3 advisories ([doctrine](doctrine/human-asks.md) v5) | done | none | wt/ask-writing | 2704724 | skill 2026.10.24.2; 649 tests green (6 new, tests/test_human_asks.py WritingTests) | 2026-10-24 | none |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent from agent_team) | ticket-37 SessionStart never shows other repos' state (L-18): `attention_lines` prints only the cwd repo's mess/stale, no `N more`; `repo_state.py` on request | done | none | wt/current-repo-attention | 65c7e2b | skill 2026.10.24.3; merged ec45219; 650 tests green; live attention_lines from agent_team empty | 2026-10-24 | none |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent from agent_team EPIC-8 E8-S8) | ticket-38 Asks in human format (agent_team L-14): `impact:`, `risk:`, `why <who>:` in `--json`; advisory if impact/risk/recommend missing ([doctrine](doctrine/human-asks.md) v6) | done | none | wt/ask-human-format | e17701e | skill 2026.10.24.4; 653 tests green (3 new + 3 updated, tests/test_human_asks.py) | 2026-10-24 | none |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent from agent_team EPIC-8 E8-S10) | ticket-39 Finish the job (agent_team L-16): no end-of-turn offers; global block rule 5, SKILL.md, preamble ([doctrine](doctrine/human-asks.md) v7) | done | none | wt/finish-the-job | e1619ca | skill 2026.10.24.5; tests green (1 new, tests/test_default_behaviors.py) | 2026-10-24 | none |
| draft | Ticket worker | worker (Sonnet 5.5, seat pool) | ticket-40 Parked work leaves the way (L-19): park = verified `archive/<name>` tag, branch/worktree deleted, never asked again; skill doctrine + `auto_return.py` (CHANGELOG 2026.10.24.6) | done | none | wt/park-archives | b7e70df | skill 2026.10.24.6; merged ecb30c5; 655 tests green; archived-tag refs never reported; 3 branches archived 2026-10-24 | 2026-10-24 | none |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent from agent_team) | ticket-41 Whole-repo PR/CI policy without a `Deploy gate:` flagged at SessionStart (`deploy_gate.attention`; zenod stranded spine answers); pre-2026.10.16.12 vendored copies flagged whatever their age; doctrine: fix the deploy trigger (`paths-ignore` docs) + declare the gate, never PRs for the whole repo (L-12) | done | none | main-direct | b28a3f2 | skill 2026.10.25.1; 724 tests green (WholeRepoPolicy 5 new, vendored 1 new) | 2026-10-25 | none |
