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
Last attempted: 2026-10-25 DM wake run_57aac66f: E7-S1 found merged (d37094b); 724 tests OK, graph --strict 0; E7-3 rollout check dispatched (run_c59cfb38)
Result: E7-1, E7-2 met on main; E7-3 open (rollout to every installer target, reachable/unreachable list)
Evidence: d08988d, ad62e8f, a6bf501; merge d37094b
Waiting on: none
Approved work: E7-S1 (brief docs/handoffs/E14-S1.md in agent_team)
Next action: verify the E7-3 rollout table (docs/epic7/rollout-2026-10-25.md), then write the Outcome
Source revision: main
Verified at: 2026-10-25

## Non-Goals

Not changing the agent_team console (it complies in its own repo, EPIC-14), and not changing any epic's Status in any repo.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker (Sonnet 5.5, seat1) | E7-S1 run_state contract: `--json` fields, doctrine, advisories, tests, release and rollout; brief docs/handoffs/E14-S1.md (agent_team) | done | none | merged d37094b (branch gone) | main | d08988d, ad62e8f, a6bf501; on main via d37094b; 724 tests OK 2026-10-25 | 2026-10-25 | none |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |
| 2026-10-24 | accepted | New epics scaffold `draft`; only the user readies; unknown Status = planning; no draft-to-ready author warning (a file validator cannot know the author) | nothing may auto-queue; rule in spine-model.md Running | ad62e8f | an author signal exists |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
