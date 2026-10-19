# EPIC-3: Epic log

Spine profile: compact
Ticket backend: github
Spine dialect: v1
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-3-EPIC-LOG.md
Spine ID: epicspine-epic-log
Spine Type: branch
Root spine: [EPIC-2 EpicSpine operating system](EPIC-2-OPERATING-SYSTEM.md)
Parent spine: [EPIC-2 EpicSpine operating system](EPIC-2-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main

## Current State

Owner: EPIC-3 delivery manager (thread mcp:e9568396-d334-4a6b-bc0c-ab93b4a0fb6b)
Status: active
Last attempted: 2026-10-19 skill tools round 1 (b19f284) reviewed; round 2 running (repo-relative links, safe gate rollout, test dirs); scope added: `## Goal` + `## Done means`, `Doctrine:` header, status words (Decisions)
Result: 503 tests OK on wt/epic-log; not merged
Evidence: docs/handoffs/2026-10-19-spine-conformance.md
Waiting on: worker wt/epic-log round 2
Approved work: E3-1 to E3-5 (user, 2026-10-19)
Next action: verify round 2; ship Goal/Done means as round 3; merge; then launch the poly-maker migration thread
Source revision: main
Verified at: 2026-10-19

## Mission

Goal: every goal in every repo is an EPIC with a code, a one-line goal and success criteria, hung in one tree from the repo's root, and agents keep that tree true.

Why: Jordi and the agent_team console must see what is open, settled and archived, and attach personas to active goals. "All repos on latest" was said while goal docs (poly-maker E4) sat outside any tree.

## Non-Goals

No rename of existing files or header fields. Migration changes structure only (header, links, state, checkboxes), never what a goal means. No cross-repo portfolio root yet. agent_team console code is agent_team's work; this epic delivers the contract it reads.

## Definition Of Done

- [ ] E3-1 The skill ships it: the definition, `spine_new.py`, `spines.py --json` and the commit check are released on main with tests green.
- [ ] E3-2 Agents keep it true: every new ask is answered with a `Goal: EPIC-<n>` line and lands in the tree; done or replaced goals close; goals active but untouched 14 days are flagged. Measured by tests plus 3 fresh sessions in different repos.
- [ ] E3-3 Every repo conforms: `spines.py --json` on each repo on vps1 shows 0 orphans and 0 mismatches, or each exception is recorded in that repo; repos without a root were offered one and the answer is recorded. Proof: a published before/after table.
- [ ] E3-4 The console sees it: the agent_team milestone picker lists poly-maker E4, read from `spines.py --json`.
- [ ] E3-5 "On latest EpicSpine" means installed and conforming (E3-3 green): an Operating Learning in EPIC-2, and no current instruction says otherwise.

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker (Sonnet 5.5, seat pool) | E3-1 skill tools: definition, `spine_new`, tree gate, `spines --json`; release 2026.10.19.1 | draft | none | wt/epic-log | main | r1 b19f284: 503 tests OK; review: repo-relative Parent spine unresolved (agent_team m2-m5 orphaned), gate would block legacy-doc edits in unmigrated repos, test fixtures counted; r2 dispatched | 2026-10-19 | verify r2; r3: `## Goal` + `## Done means` in template and `spine_new`, `## Mission` alias, trackable gate requires non-empty Goal on new/migrated spines (ticket-copy DoD advisory), `Doctrine:` header written by `spine_new` + doctrine table in spine-model.md; `spines --json` gains `doctrine`, `goal`, `done_means`, `expected_sections`, `missing_sections`; console badge rule (Status only) documented; align wording to "nested markdowns, judgment"; merge |
| draft | Ticket worker | unassigned | E3-2 living tree: always-on `Goal: EPIC-<n>` rule; Record duties (new goal -> `spine_new`, done -> roll up, replaced -> `Superseded by:`); `spines --active`; stale goals 14 d flagged; `spine_new` assigns the next EPIC code; Done means stays outcomes, tickets in the ledger; lean Current State limit | draft | E3-1 | none | main | queued 2026-10-19 by user | 2026-10-19 | dispatch after E3-1 merges |
| draft | Repo delivery manager | poly-maker thread | E3-3 migrate poly-maker (EPIC.md, EPIC0.md, E4, 31 orphans); E4 gets `EPIC-4: One logger` title, plain Goal + Done means and `Doctrine:` set, one consistent status (`deferred` if Jordi paused it; badge blocked vs `deferred`); supersedes agent_team reshape d9c21a0/c43c557; launch E4 only via an agent_team console persona once it conforms (agent_team L-2); Jordi confirms the wording before commit; coordinate with the one-logger session | draft | E3-1 | none | main | 31 orphans, root without Spine ID | 2026-10-19 | launch thread in the poly-maker project |
| draft | Repo delivery manager | per-repo threads | E3-3 migrate zenod (46), idea_scraper (25, no root), infra-vps (11 + 1 mismatch), obsidian-brain (8, no root), abnb-agent (2), zenod-cloud (1, no root) | draft | E3-1 | none | main | counts from r1 scan 2026-10-19 | 2026-10-19 | launch after poly-maker proves the brief |
| draft | Delivery manager | /root delivery manager | E3-3 conformance table, before/after per repo | draft | E3-3 migrations | none | main | before column: r1 scan 2026-10-19 | 2026-10-19 | publish when migrations land |
| draft | Repo delivery manager | agent_team thread d14c8f2e | E3-4 console picker reads `spines.py --json`; Overview shows Goal and Done means above the ticket boxes; renders per `doctrine`, flags `missing_sections`; badge from `Status:` only | draft | E3-1 | none | main | picker guesses by path (repos.ts:163); console shows E4 as 15 tickets + state, no purpose (2026-10-19) | 2026-10-19 | after r3 merges: send field list + poly-maker example output to agent_team thread d14c8f2e |
| draft | Delivery manager | /root delivery manager | E3-5 learning "on latest = installed and conforming" + supersede sweep | draft | E3-3 | none | main | none | 2026-10-19 | write when the table is green |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-19 | accepted | Nested markdowns, judgment | Progress inside a goal is written in its spine; a new measurable objective worked over several pushes gets a new leaf markdown linked from its parent. Full decision in EPIC-2 Decisions. | user 2026-10-19 | never |
| 2026-10-19 | accepted | Every goal has a code | A goal is named `EPIC-<n>: <short name>`, states its goal in one line and lists measurable success criteria; without a code it cannot be discussed. | user 2026-10-19 | never |
| 2026-10-19 | accepted | Goal and Done means open every spine | Right after the header: `## Goal` (1-2 plain sentences: what changes and why it matters to Jordi, readable without the code), then `## Done means` (2-5 measurable outcomes in human terms) = the DoD's top criteria; tickets live in the Issue Ledger, ticket boxes only under the outcomes. Commit check (trackable) requires a non-empty Goal on new and migrated spines; ticket-copy DoD is advisory; `## Mission` accepted as alias. Cause: console showed poly-maker E4 as 15 tickets with no purpose, Mission a technical target, DoD 1:1 tickets, status contradictory. | user 2026-10-19 via previous manager thread | never |
| 2026-10-19 | accepted | Spines record their doctrine | New header line `Doctrine: <skill release that defined the section set>`, kept separate from `Spine dialect:` (that governs the acceptance workflow, not sections). `spine_new` writes it, migrations set it, absent = legacy (pre-Goal). spine-model.md holds a table of required sections per doctrine; `spines --json` emits `doctrine`, `expected_sections`, `missing_sections` so the console renders what the version promises and flags gaps. | user 2026-10-19 via agent_team manager | a second shape change needs a migration path |
| 2026-10-19 | accepted | One status word per state | `Status:` in Current State is the only status source: paused by Jordi = `deferred` (spine_fix maps on hold/paused/parked to it); `blocked` = waiting on a named external dependency; `Waiting on:` is context and never implies blocked. The console badge reads `Status:` only. | user 2026-10-19 via agent_team manager (E4 showed Blocked vs `deferred`) | never |
| 2026-10-19 | accepted | agent_team does not rewrite E4 | agent_team aligns to EPIC-3 doctrine; the E4 rewrite belongs to the E3-3 poly-maker thread; agent_team's earlier reshape (poly-maker d9c21a0, c43c557: Spine ID, Current State, 15-box ticket DoD) is superseded by that migration. | agent_team manager 2026-10-19 | never |
