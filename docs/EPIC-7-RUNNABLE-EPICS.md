# EPIC-7: Runnable epics: run_state contract

Spine profile: compact
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-7-RUNNABLE-EPICS.md
Spine ID: runnable-epics-run-state-contract
Root spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Parent spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main
Integration policy: main-direct

## Goal

An epic's own Status says whether a wake may work it: `spines.py --json` carries `run_state` (planning | ready | running | parked | finished), `runnable` and `has_children` per node, the doctrine says a wake works only runnable epics and a spine with children steers, and the validator advises on `active` with no start recorded and `draft` with active rows. No new flag. Origin: agent_team docs/spines/epic-14-runnable-epics.md (E14-S1, Jordi 2026-10-24: switching a Delivery Manager on must not run all ~10 `active`/`ready` epics and 122 ledger rows).

## Serves

[EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md): the skill owns the doctrine for which epics a wake may run, so every repo's Delivery Manager and the agent_team console read the same rule; serves agent_team EPIC-14 (E14-1, step E14-S1).

## Done means

- [x] E7-1 `spines.py --json` adds `run_state`, `runnable`, `has_children` to every node exactly per the Status table in references/spine-model.md "Running"; one test per table row and for `has_children`; verified by the full suite and the agent_team root map sample
- [x] E7-2 `validate_spine.py` warns (advisory, never `--strict`-promoted) for `Status: active` with no start recorded and for a `draft` epic with `active` ledger rows, one positive and one negative fixture each
- [x] E7-3 the new version is rolled out to every machine config dir and repo the installer covers, with the reachable and unreachable list reported (not claimed as all); evidence: [rollout table](epic7/rollout-2026-10-25.md): 7 reachable config dirs (vps3 x3 Claude, vps1 x3 Claude + Codex) on 2026.10.25.1, 17 of 19 repo blocks current; unreachable: Jordi's Mac (ssh timeout), vps1-egress (no key); lagging block text: tax-assist-research, whatgpt_webflow_export (own repos' threads)

## Current State

Owner: Delivery Manager (agent-team console)
Status: active
Last attempted: 2026-10-25 DM wake run_21b34e03: removed agent-written Verdict/Closed (only Jordi marks the verdict); 2026-10-25 DM wake run_57aac66f: E7-S1 merged (d37094b); E7-3 rollout verified (run_c59cfb38, 0c6c0f9; DM re-checked vps3 + vps1 skill links, VERSION 2026.10.25.1)
Result: E7-1..E7-3 met; reopened for defect E7-S2 (spine Status `review` rewritten to active by the hook)
Evidence: merge d37094b; 0c6c0f9 [rollout table](epic7/rollout-2026-10-25.md); 724 tests OK
Waiting on: nobody
Approved work: E7-S1 (brief docs/handoffs/E14-S1.md in agent_team)
Next action: E7-S2 (Status review legal, run_state not runnable) dispatched by run_21b34e03; then Status review and Jordi marks the verdict
Source revision: main
Verified at: 2026-10-25

## Outcome

Outcome: `spines.py --json` tells any console whether an epic may run (`run_state`, `runnable`, `has_children`), new epics scaffold `draft` until the user stamps them ready, two advisories catch active-without-start and draft-with-active-rows, and the release is live on every reachable config dir (vps3, vps1: 7 dirs, 2026.10.25.1).
Risk: Jordi's Mac unreachable (ssh timeout) so its install is unverified; tax-assist-research AGENTS.md block migrated on vps1 but uncommitted; whatgpt_webflow_export has no block until a session opens there.

| Done means | Evidence |
|---|---|
| E7-1 | d08988d (run_state, runnable, has_children + tests); merge d37094b |
| E7-2 | d08988d (run-state advisories, positive/negative fixtures); 724 tests OK on main 2026-10-25 |
| E7-3 | 0c6c0f9 [rollout table](epic7/rollout-2026-10-25.md): 7 reachable config dirs on 2026.10.25.1; Mac and vps1-egress listed unreachable |

## Non-Goals

Not changing the agent_team console (it complies in its own repo, EPIC-14), and not changing any epic's Status in any repo.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker (Sonnet 5.5, seat1) | E7-S1 run_state contract: `--json` fields, doctrine, advisories, tests, release and rollout; brief docs/handoffs/E14-S1.md (agent_team) | done | none | merged d37094b (branch gone) | main | d08988d, ad62e8f, a6bf501; on main via d37094b; 724 tests OK 2026-10-25 | 2026-10-25 | none |
| E7-S2 | Ticket worker | worker run_84d3be55 (Sonnet 5.5, seat2) | epic Status `review` (Outcome written, awaiting Jordi's verdict) is a trackable spine Status: spine_fix stops rewriting it to active; run_state = not runnable; validator, doctrine, tests, release | review | none | e7-s2 | main | c952215 (branch e7-s2, skill 2026.10.25.2; 728 tests OK; EPIC-6 kept `review` under the branch hook: f88e927) | 2026-10-25 | DM verifies and merges |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |
| 2026-10-25 | accepted | decided by Delivery Manager: open E7-S2 to make spine `Status: review` legal (console protocol sets it after the Outcome; the pre-commit hook rewrote it to active) — why: status must be true, and a review epic must not run — rollback: revert the E7-S2 merge | known defect fix inside this epic's contract | 51c12e6 | never |
| 2026-10-24 | accepted | New epics scaffold `draft`; only the user readies; unknown Status = planning; no draft-to-ready author warning (a file validator cannot know the author) | nothing may auto-queue; rule in spine-model.md Running | ad62e8f | an author signal exists |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
