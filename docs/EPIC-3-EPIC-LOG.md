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
Last attempted: 2026-10-19 E3-1 round 2 merged (cab199a, 4639aa9; MANIFEST fixed 88f00fa: worker had committed 4 __pycache__ entries); round 3 (wording, code rule, status words, manifest skip) next
Result: main @ 88f00fa: 507 tests OK (1 skipped; test_url_gate localhost flakes under full-suite load, passes alone); own repo 0 orphans 0 mismatches; agent_team m2-m5 are nodes, 4 mismatches (root Spine Map missing: agent_team's migration)
Evidence: docs/handoffs/2026-10-19-spine-conformance.md
Waiting on: E3-1 round 3 worker
Approved work: E3-1 to E3-5 (user, 2026-10-19)
Next action: verify and merge round 3, then tell EPIC-4 SKILL.md/spine-model.md are free; dispatch E3-2; send the E3-4 contract to agent_team d14c8f2e; launch the poly-maker migration (never mentioning E4)
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
| draft | Ticket worker | worker (Sonnet 5.5, seat pool) | E3-1 skill tools: definition, `spine_new`, tree gate, `spines --json`; release 2026.10.19.1 | active | none | wt/epic-log-r3 | main | r1+r2 merged on main (cab199a, 4639aa9), MANIFEST fixed 88f00fa, 507 OK; scripts handed to EPIC-4 | 2026-10-19 | r3 (SKILL.md, spine-model.md, manifest script only): nested markdowns + judgment, `EPIC-<n>: <name>` code rule, status words (ready before launch, persona launch = active, paused = deferred, badge from `Status:`), manifest skips __pycache__; verify, merge |
| draft | Ticket worker | unassigned | E3-2 living tree: always-on `Goal: EPIC-<n>` rule; Record duties (new goal -> `spine_new`, done -> roll up, replaced -> `Superseded by:`); `spines --active`; stale goals 14 d flagged; `spine_new` assigns the next EPIC code; lean Current State limit | draft | E3-1 | none | main | queued 2026-10-19 by user; EPIC-4 handed spines.py/spine_new.py/pre_commit.py back until its step 2 is approved (277d585): leave room under the spines.py 200-line budget (EPIC-4 step 3 adds doctrine/goal/serves/done_means/contributes/missing_sections) | 2026-10-19 | dispatch after r3 merges; when rules settle send EPIC-4 manager (61d2777c) the living-tree rules in shortest form; hand the scripts back when EPIC-4 asks |
| draft | Repo delivery manager | poly-maker thread | E3-3 migrate poly-maker (EPIC.md, EPIC0.md, 31 orphans); E4 excluded: a poly-maker thread brings E4 to Doctrine 2 as EPIC-4's compliance test (E4-4), so this brief never mentions E4 (L-14); coordinate with the one-logger session | draft | E3-1 | none | main | 31 orphans, root without Spine ID | 2026-10-19 | launch thread in the poly-maker project |
| draft | Repo delivery manager | per-repo threads | E3-3 migrate zenod (46), idea_scraper (25, no root), infra-vps (11 + 1 mismatch), obsidian-brain (8, no root), abnb-agent (2), zenod-cloud (1, no root) | draft | E3-1 | none | main | counts from r1 scan 2026-10-19 | 2026-10-19 | launch after poly-maker proves the brief |
| draft | Delivery manager | /root delivery manager | E3-3 conformance table, before/after per repo | draft | E3-3 migrations | none | main | before column: r1 scan 2026-10-19 | 2026-10-19 | publish when migrations land |
| draft | Repo delivery manager | agent_team thread d14c8f2e | E3-4 console picker reads `spines.py --json`; badge from `Status:` only (Goal/Done means view is EPIC-4 E4-3) | draft | E3-1 | none | main | picker guesses by path (repos.ts:163); console shows E4 as 15 tickets + state, no purpose (2026-10-19) | 2026-10-19 | after E3-1 merges: send the `spines.py --json` field list + poly-maker example to agent_team thread d14c8f2e |
| draft | Delivery manager | /root delivery manager | E3-5 learning "on latest = installed and conforming" + supersede sweep | draft | E3-3 | none | main | none | 2026-10-19 | write when the table is green |

## Decisions

Goal / Done means and doctrine versioning moved to [EPIC-4](EPIC-4-DOCTRINE-2.md) on 2026-10-19 (Jordi); rows marked superseded live there now.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-19 | accepted | Nested markdowns, judgment | Progress inside a goal is written in its spine; a new measurable objective worked over several pushes gets a new leaf markdown linked from its parent. Full decision in EPIC-2 Decisions. | user 2026-10-19 | never |
| 2026-10-19 | accepted | Every goal has a code | A goal is named `EPIC-<n>: <short name>`, states its goal in one line and lists measurable success criteria; without a code it cannot be discussed. | user 2026-10-19 | never |
| 2026-10-19 | superseded | Goal and Done means open every spine | Right after the header: `## Goal` (1-2 plain sentences: what changes and why it matters to Jordi, readable without the code), then `## Done means` (2-5 measurable outcomes in human terms) = the DoD's top criteria; tickets live in the Issue Ledger, ticket boxes only under the outcomes. Commit check (trackable) requires a non-empty Goal on new and migrated spines; ticket-copy DoD is advisory; `## Mission` accepted as alias. Cause: console showed poly-maker E4 as 15 tickets with no purpose, Mission a technical target, DoD 1:1 tickets, status contradictory. | user 2026-10-19 via previous manager thread | never |
| 2026-10-19 | superseded by `Spine format` | Spines record their doctrine | New header line `Doctrine: <skill release that defined the section set>`, kept separate from `Spine dialect:` (that governs the acceptance workflow, not sections). `spine_new` writes it, migrations set it, absent = legacy (pre-Goal). spine-model.md holds a table of required sections per doctrine; `spines --json` emits `doctrine`, `expected_sections`, `missing_sections` so the console renders what the version promises and flags gaps. | user 2026-10-19 via agent_team manager | a second shape change needs a migration path |
| 2026-10-19 | accepted | One status word per state | `Status:` in Current State is the only status source: paused by Jordi = `deferred` (spine_fix maps on hold/paused/parked to it); `blocked` = waiting on a named external dependency; `Waiting on:` is context and never implies blocked. The console badge reads `Status:` only. | user 2026-10-19 via agent_team manager (E4 showed Blocked vs `deferred`) | never |
| 2026-10-19 | superseded by E4 single writer | agent_team does not rewrite E4 | agent_team aligns to EPIC-3 doctrine; the E4 rewrite belongs to the E3-3 poly-maker thread; agent_team's earlier reshape (poly-maker d9c21a0, c43c557: Spine ID, Current State, 15-box ticket DoD) is superseded by that migration. | agent_team manager 2026-10-19 | never |
| 2026-10-19 | superseded by EPIC-4 `Doctrine: <n>` | `Spine format: 2` extends format 1 | Header `Spine format: <n>`, undeclared = 1; format 1 (Mission + DoD) stays valid unchanged. Format 2 adds a human layer reading as one story root to leaf: Goal (`## Mission` counts), place in the tree (1-2 sentences on how it serves the parent's goal, linked), one plain sentence per Spine Map child on what it contributes, Done means (2-5 measurable outcomes above tickets), coded `EPIC-<n>:` title and one status. `spines --json`: `format`, `goal`, `serves`, `done_means`, per-child `contributes`. Gate enforces 2 on new and migrated spines only. `Spine dialect:` stays the workflow axis. Replaces the `Doctrine:` line. | Jordi 2026-10-19 | never |
| 2026-10-19 | superseded by L-14 (a poly-maker thread writes E4) | E4 single writer | Jordi's agent_team thread "E4 test in polymaker" (d14c8f2e) owns E4's content; EPIC-3 checks only E4's structure and format, never its intent. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Launch is the start order | Launching a persona on a spine from the console is the start order: before launch Status is `ready`, launch makes it `active`, the persona carries the goal to completion. Written where status is defined in the skill. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Jordi talks to EPIC-3's manager directly | From now on EPIC-3 and spine-format questions come straight to this thread, not via the previous manager. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Scope split with EPIC-4 | EPIC-4 (Doctrine 2, own manager) owns Goal, Serves, children's contributes, Done means and `Doctrine: <n>` (absent = 1). EPIC-3 keeps the tree tools, the EPIC code rule, wording alignment, status words, every repo's conformance, the console picker and the "on latest" learning. Merge order: EPIC-3 round 2 (+ trimmed round 3) first, then EPIC-4 gets spines.py/spine_new.py/pre_commit.py; never two workers on them at once. Roles per EPIC-2 L-14; poly-maker E4 is EPIC-4's compliance test, so EPIC-3 never briefs it. | Jordi 2026-10-19 via orchestrator | never |
