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
Last attempted: 2026-10-19 skill tools round 1 (b19f284) reviewed; round 2 running (repo-relative links, safe gate rollout, test dirs); scope added: `## Goal` + `## Done means` (Decisions)
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
| draft | Ticket worker | worker (Sonnet 5.5, seat pool) | E3-1 skill tools: definition, `spine_new`, tree gate, `spines --json`; release 2026.10.19.1 | draft | none | wt/epic-log | main | r1 b19f284: 503 tests OK; review: repo-relative Parent spine unresolved (agent_team m2-m5 orphaned), gate would block legacy-doc edits in unmigrated repos, test fixtures counted; r2 dispatched | 2026-10-19 | verify r2; r3: `## Goal` + `## Done means` in template and `spine_new`, `## Mission` alias, trackable gate requires non-empty Goal on new/migrated spines (ticket-copy DoD advisory), `spines --json` gains `goal` and `done_means`; align wording to "nested markdowns, judgment"; merge |
| draft | Ticket worker | unassigned | E3-2 living tree: always-on `Goal: EPIC-<n>` rule; Record duties (new goal -> `spine_new`, done -> roll up, replaced -> `Superseded by:`); `spines --active`; stale goals 14 d flagged; `spine_new` assigns the next EPIC code; Done means stays outcomes, tickets in the ledger; lean Current State limit | draft | E3-1 | none | main | queued 2026-10-19 by user | 2026-10-19 | dispatch after E3-1 merges |
| draft | Repo delivery manager | poly-maker thread | E3-3 migrate poly-maker (EPIC.md, EPIC0.md, E4, 31 orphans); E4 gets `EPIC-4: One logger` title, plain Goal + Done means and one consistent status (badge blocked vs `deferred`); Jordi confirms the wording before commit; coordinate with the one-logger session | draft | E3-1 | none | main | 31 orphans, root without Spine ID | 2026-10-19 | launch thread in the poly-maker project |
| draft | Repo delivery manager | per-repo threads | E3-3 migrate zenod (46), idea_scraper (25, no root), infra-vps (11 + 1 mismatch), obsidian-brain (8, no root), abnb-agent (2), zenod-cloud (1, no root) | draft | E3-1 | none | main | counts from r1 scan 2026-10-19 | 2026-10-19 | launch after poly-maker proves the brief |
| draft | Delivery manager | /root delivery manager | E3-3 conformance table, before/after per repo | draft | E3-3 migrations | none | main | before column: r1 scan 2026-10-19 | 2026-10-19 | publish when migrations land |
| draft | Repo delivery manager | agent_team thread | E3-4 console picker reads `spines.py --json`; Overview shows Goal and Done means above the ticket boxes | draft | E3-1 | none | main | picker guesses by path (repos.ts:163); console shows E4 as 15 tickets + state, no purpose (2026-10-19) | 2026-10-19 | hand off after E3-1 merges |
| draft | Delivery manager | /root delivery manager | E3-5 learning "on latest = installed and conforming" + supersede sweep | draft | E3-3 | none | main | none | 2026-10-19 | write when the table is green |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-19 | accepted | Nested markdowns, judgment | Progress inside a goal is written in its spine; a new measurable objective worked over several pushes gets a new leaf markdown linked from its parent. Full decision in EPIC-2 Decisions. | user 2026-10-19 | never |
| 2026-10-19 | accepted | Every goal has a code | A goal is named `EPIC-<n>: <short name>`, states its goal in one line and lists measurable success criteria; without a code it cannot be discussed. | user 2026-10-19 | never |
| 2026-10-19 | accepted | Goal and Done means open every spine | Right after the header: `## Goal` (1-2 plain sentences: what changes and why it matters to Jordi, readable without the code), then `## Done means` (2-5 measurable outcomes in human terms) = the DoD's top criteria; tickets live in the Issue Ledger, ticket boxes only under the outcomes. Commit check (trackable) requires a non-empty Goal on new and migrated spines; ticket-copy DoD is advisory; `## Mission` accepted as alias. Cause: console showed poly-maker E4 as 15 tickets with no purpose, Mission a technical target, DoD 1:1 tickets, status contradictory. | user 2026-10-19 via previous manager thread | never |
