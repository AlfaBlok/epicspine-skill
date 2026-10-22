# Decisions of the epic log: detail

Page of [EPIC-3](../EPIC-3-EPIC-LOG.md). The Decisions table there keeps one line per decision; the full Durable Summary of each row over 200 characters, as it stood in the table, is here. Decisions are numbered by row position in the table (rows that fit stay in the table only).

## D 1

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Nested markdowns, judgment
- **Durable Summary:** Progress inside a goal is written in its spine; a new measurable objective worked over several pushes gets a new spine markdown linked from its parent (L-16 wording). Full decision in EPIC-0 Decisions.
- **Evidence:** user 2026-10-19
- **Revisit When:** never

## D 3

- **Date:** 2026-10-19
- **Outcome:** superseded
- **Decision / Attempt:** Goal and Done means open every spine
- **Durable Summary:** Right after the header: `## Goal` (1-2 plain sentences: what changes and why it matters to Jordi, readable without the code), then `## Done means` (2-5 measurable outcomes in human terms) = the DoD's top criteria; tickets live in the Issue Ledger, ticket boxes only under the outcomes. Commit check (trackable) requires a non-empty Goal on new and migrated spines; ticket-copy DoD is advisory; `## Mission` accepted as alias. Cause: console showed poly-maker E4 as 15 tickets with no purpose, Mission a technical target, DoD 1:1 tickets, status contradictory.
- **Evidence:** user 2026-10-19 via previous manager thread
- **Revisit When:** never

## D 4

- **Date:** 2026-10-19
- **Outcome:** superseded by `Spine format`
- **Decision / Attempt:** Spines record their doctrine
- **Durable Summary:** New header line `Doctrine: <skill release that defined the section set>`, kept separate from `Spine dialect:` (that governs the acceptance workflow, not sections). `spine_new` writes it, migrations set it, absent = legacy (pre-Goal). spine-model.md holds a table of required sections per doctrine; `spines --json` emits `doctrine`, `expected_sections`, `missing_sections` so the console renders what the version promises and flags gaps.
- **Evidence:** user 2026-10-19 via agent_team manager
- **Revisit When:** a second shape change needs a migration path

## D 5

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** One status word per state
- **Durable Summary:** `Status:` in Current State is the only status source: paused by Jordi = `deferred` (spine_fix maps on hold/paused/parked to it); `blocked` = waiting on a named external dependency; `Waiting on:` is context and never implies blocked. The console badge reads `Status:` only.
- **Evidence:** user 2026-10-19 via agent_team manager (E4 showed Blocked vs `deferred`)
- **Revisit When:** never

## D 6

- **Date:** 2026-10-19
- **Outcome:** superseded by E4 single writer
- **Decision / Attempt:** agent_team does not rewrite E4
- **Durable Summary:** agent_team aligns to EPIC-3 doctrine; the E4 rewrite belongs to the E3-3 poly-maker thread; agent_team's earlier reshape (poly-maker d9c21a0, c43c557: Spine ID, Current State, 15-box ticket DoD) is superseded by that migration.
- **Evidence:** agent_team manager 2026-10-19
- **Revisit When:** never

## D 7

- **Date:** 2026-10-19
- **Outcome:** superseded by EPIC-4 `Doctrine: <n>`
- **Decision / Attempt:** `Spine format: 2` extends format 1
- **Durable Summary:** Header `Spine format: <n>`, undeclared = 1; format 1 (Mission + DoD) stays valid unchanged. Format 2 adds a human layer reading as one story root to leaf: Goal (`## Mission` counts), place in the tree (1-2 sentences on how it serves the parent's goal, linked), one plain sentence per Spine Map child on what it contributes, Done means (2-5 measurable outcomes above tickets), coded `EPIC-<n>:` title and one status. `spines --json`: `format`, `goal`, `serves`, `done_means`, per-child `contributes`. Gate enforces 2 on new and migrated spines only. `Spine dialect:` stays the workflow axis. Replaces the `Doctrine:` line.
- **Evidence:** Jordi 2026-10-19
- **Revisit When:** never

## D 9

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Launch is the start order
- **Durable Summary:** Launching a persona on a spine from the console is the start order: before launch Status is `ready`, launch makes it `active`, the persona carries the goal to completion. Written where status is defined in the skill.
- **Evidence:** Jordi 2026-10-19
- **Revisit When:** never

## D 11

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Scope split with EPIC-4
- **Durable Summary:** EPIC-4 (Doctrine 2, own manager) owns Goal, Serves, children's contributes, Done means and `Doctrine: <n>` (absent = 1). EPIC-3 keeps the tree tools, the EPIC code rule, wording alignment, status words, every repo's conformance, the console picker and the "on latest" learning. Merge order: EPIC-3 round 2 (+ trimmed round 3) first, then EPIC-4 gets spines.py/spine_new.py/pre_commit.py; never two workers on them at once. Roles per EPIC-0 L-14; poly-maker E4 is EPIC-4's compliance test, so EPIC-3 never briefs it.
- **Evidence:** Jordi 2026-10-19 via orchestrator
- **Revisit When:** never

## D 12

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Split write surfaces with EPIC-4
- **Durable Summary:** While E3-2 runs, EPIC-4 writes SKILL.md and spine-model.md (doctrine page), and EPIC-3 writes the scripts, global-block.md and spine-creation.md; the doctrine points to the living-tree mechanics and does not restate them. Never two workers on one file (L-10).
- **Evidence:** Jordi's merge order 2026-10-19; EPIC-4 handback 277d585
- **Revisit When:** EPIC-4 step 2 approved

## D 13

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Living-tree rules (E3-2, release 2026.10.19.3)
- **Durable Summary:** 1. Every new ask is answered with `Goal: EPIC-<n>`: an open spine from `spines.py --active`, or a new one from `spine_new.py` (next code, never 0; root is EPIC-0). 2. Done closes (`Status: done`, parent rolls up); replaced gets `Superseded by: <link>` + `Status: done` (gate blocks a non-goal link). 3. Active/blocked with no commit for 14+ days = stale (`--active`, JSON `stale`, attention line from the 15-min background sync; SessionStart only prints). 4. Stale goals are reported to the user (keep, close or supersede), never closed silently. 5. Commit gate warns when Current State exceeds 12 lines. Handover: spines.py, spine_new.py, pre_commit.py, epic_log.py belong to EPIC-4 step 3 from 61d7e03; known edges: an out-of-repo `Superseded by:` link raises in pre_commit `goal_notes`, and `spine_new --code 0` is not rejected.
- **Evidence:** E3-2 merge 61d7e03
- **Revisit When:** EPIC-4 doctrine changes a rule
