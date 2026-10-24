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

- [ ] E7-1 `spines.py --json` adds `run_state`, `runnable`, `has_children` to every node exactly per the Status table in references/spine-model.md "Running"; one test per table row and for `has_children`; verified by the full suite and the agent_team root map sample
- [ ] E7-2 `validate_spine.py` warns (advisory, never `--strict`-promoted) for `Status: active` with no start recorded and for a `draft` epic with `active` ledger rows, one positive and one negative fixture each
- [ ] E7-3 the new version is rolled out to every machine config dir and repo the installer covers, with the reachable and unreachable list reported (not claimed as all)

## Current State

Owner: Delivery Manager (agent_team brief docs/handoffs/E14-S1.md)
Status: active
Last attempted: 2026-10-24 E7-S1 Ticket worker (Sonnet 5.5) started in worktree wt/e14-s1
Result: contract, doctrine, advisories and tests built; rollout pending
Evidence: EPIC-0-OPERATING-SYSTEM.md
Waiting on: none
Approved work: E7-S1 (brief docs/handoffs/E14-S1.md in agent_team)
Next action: Delivery manager verifies branch e14-s1 and integrates; then agent_team codes against the contract
Source revision: branch e14-s1
Verified at: 2026-10-24

## Non-Goals

Not changing the agent_team console (it complies in its own repo, EPIC-14), and not changing any epic's Status in any repo.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker (Sonnet 5.5, seat1) | E7-S1 run_state contract: `--json` fields, doctrine, advisories, tests, release and rollout; brief docs/handoffs/E14-S1.md (agent_team) | active | none | e14-s1 | main | none yet | 2026-10-24 | verify and integrate |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
