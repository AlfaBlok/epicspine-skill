# EPIC-3: Epic log

Spine profile: compact
Ticket backend: github
Spine dialect: v1
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-3-EPIC-LOG.md
Spine ID: epicspine-epic-log
Spine Type: branch
Root spine: [EPIC-0 EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Parent spine: [EPIC-0 EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main

## Current State

Owner: EPIC-3 delivery manager (thread mcp:e9568396-d334-4a6b-bc0c-ab93b4a0fb6b)
Status: active
Last attempted: 2026-10-19 E3-2 merged (c320d91..61d7e03, release 2026.10.19.3): EPIC codes in spine_new, --active, stale goals via the 15-min background sync (SessionStart stays scan-free), Superseded by:, lean Current State warning, rule 6 Record; scripts handed to EPIC-4
Result: main @ 61d7e03, full suite with CLAUDE_CONFIG_DIR/CODEX_HOME/XDG_CONFIG_HOME isolated: 517 tests, 516 OK; only test_url_gate localhost (pre-existing load flake, also red on main before E3-2)
Evidence: docs/handoffs/2026-10-19-spine-conformance.md
Waiting on: none
Approved work: E3-1 to E3-5 (user, 2026-10-19)
Next action: watch the poly-maker migration thread (mcp:766a969a; run 1 cancelled by a T3 restart with no changes, restarted 2026-10-19); full isolated suite on main rerunning (first run killed by the restart); E3-2 live proof: 3 fresh sessions in different repos; agent_team reports E3-4; then launch the zenod migration
Source revision: main
Verified at: 2026-10-19

## Mission

Goal: every goal in every repo is an EPIC with a code, a one-line goal and success criteria, hung in one tree from the repo's root, and agents keep that tree true.

Why: Jordi and the agent_team console must see what is open, settled and archived, and attach personas to active goals. "All repos on latest" was said while goal docs (poly-maker E4) sat outside any tree.

## Serves

[EPIC-0 EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md) wants a repository's spines to form one tree of goals, each stating its purpose and measurably accomplishable (EPIC-0 Mission). This epic makes that true: every goal is a coded EPIC in one tree per repo, kept true by agents (EPIC-0 Spine Map).

## Non-Goals

No rename of existing files or header fields. Migration changes structure only (header, links, state, checkboxes), never what a goal means. No cross-repo portfolio root yet. agent_team console code is agent_team's work; this epic delivers the contract it reads.

## Definition Of Done

- [x] E3-1 The skill ships it: the definition, `spine_new.py`, `spines.py --json` and the commit check are released on main with tests green.
- [ ] E3-2 Agents keep it true: every new ask is answered with a `Goal: EPIC-<n>` line and lands in the tree; done or replaced goals close; goals active but untouched 14 days are flagged. Measured by tests plus 3 fresh sessions in different repos.
- [ ] E3-3 Every repo conforms: `spines.py --json` on each repo on vps1 shows 0 orphans and 0 mismatches, or each exception is recorded in that repo; repos without a root were offered one and the answer is recorded. Proof: a published before/after table.
- [ ] E3-4 The console sees it: the agent_team milestone picker lists poly-maker E4, read from `spines.py --json`.
- [ ] E3-5 "On latest EpicSpine" means installed and conforming (E3-3 green): an Operating Learning in EPIC-0, and no current instruction says otherwise.

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker (Sonnet 5.5, seat pool) | E3-1 skill tools: definition, `spine_new`, tree gate, `spines --json`; release 2026.10.19.1 | done | none | none | main | r1+r2+r3 merged (cab199a, 4639aa9, 88f00fa, 52cdd31..20b4602), release 2026.10.19.2; 508 tests, url_gate flakes only under host load | 2026-10-19 | none |
| draft | Ticket worker | worker (Sonnet 5.5, native subagent; seat pool unavailable) | E3-2 living tree: `Goal: EPIC-<n>` rule, Record duties, `spines --active`, 14 d stale flag, `spine_new` assigns the next code; release 2026.10.19.3 [detail](epic-log/steps.md#ticket-2) | active | E3-1 | none | main | merged 61d7e03 (2026.10.19.3); r2 fixed a +2-9 s SessionStart scan; tests run with CLAUDE_CONFIG_DIR/CODEX_HOME/XDG_CONFIG_HOME isolated (EPIC-4 step 9 config leak) | 2026-10-19 | DoD proof: 3 fresh sessions in different repos answer with a `Goal: EPIC-<n>` line; then tick E3-2 |
| draft | Repo delivery manager | poly-maker thread | E3-3 migrate poly-maker (EPIC.md, EPIC0.md, 31 orphans); E4 excluded (L-14): its own thread brings E4 to Doctrine 2 [detail](epic-log/steps.md#ticket-3) | active | E3-1 | main-direct | main | launched 2026-10-19 as thread mcp:766a969a in the poly-maker project: EPIC0.md becomes root EPIC-0, EPIC.md EPIC-1, EPIC-4 reserved [detail](epic-log/steps.md#ticket-3) | 2026-10-19 | await its report (before/after, --active, judgment calls) |
| draft | Repo delivery manager | per-repo threads | E3-3 migrate zenod (46), idea_scraper (25, no root), infra-vps (11 + 1 mismatch), obsidian-brain (8, no root), abnb-agent (2), zenod-cloud (1, no root) | draft | E3-1 | none | main | counts from r1 scan 2026-10-19 | 2026-10-19 | launch after poly-maker proves the brief |
| draft | Delivery manager | /root delivery manager | E3-3 conformance table, before/after per repo | draft | E3-3 migrations | none | main | before column: r1 scan 2026-10-19 | 2026-10-19 | publish when migrations land; per skill doctrine (was EPIC-0 L-16) unlinked pages count as orphans, measured once EPIC-4 step 3 adds page discovery to spines.py |
| draft | Repo delivery manager | agent_team thread d14c8f2e | E3-4 console picker reads `spines.py --json`; badge from `Status:` only (Goal/Done means view is EPIC-4 E4-3) | draft | E3-1 | none | main | picker guesses by path (repos.ts:163); console shows E4 as 15 tickets + state, no purpose (2026-10-19) | 2026-10-19 | contract + poly-maker example sent 2026-10-19 (picker must list flagged orphans so E4 stays visible before migration); await agent_team report |
| draft | Delivery manager | /root delivery manager | E3-5 learning "on latest = installed and conforming" + supersede sweep | draft | E3-3 | none | main | none | 2026-10-19 | write when the table is green |

## Decisions

Goal / Done means and doctrine versioning moved to [EPIC-4](EPIC-4-DOCTRINE-2.md) on 2026-10-19 (Jordi); rows marked superseded live there now.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-19 | accepted | Nested markdowns, judgment | Progress inside a goal is written in its spine; a new measurable objective over several pushes gets a new linked spine (L-16); full text in EPIC-0. [detail](epic-log/decisions.md#d1) | user 2026-10-19 | never |
| 2026-10-19 | accepted | Every goal has a code | A goal is named `EPIC-<n>: <short name>`, states its goal in one line and lists measurable success criteria; without a code it cannot be discussed. | user 2026-10-19 | never |
| 2026-10-19 | superseded | Goal and Done means open every spine | Superseded (now EPIC-4): `## Goal` then `## Done means` open every spine; the commit check requires a non-empty Goal on new and migrated spines. [detail](epic-log/decisions.md#d3) | user 2026-10-19 via previous manager thread | never |
| 2026-10-19 | superseded by `Spine format` | Spines record their doctrine | Superseded by `Spine format`: header `Doctrine: <release>` apart from `Spine dialect:`; `spine_new` writes it; `spines --json` emits `expected_sections`. [detail](epic-log/decisions.md#d4) | user 2026-10-19 via agent_team manager | a second shape change needs a migration path |
| 2026-10-19 | accepted | One status word per state | `Status:` in Current State is the only status source: paused = `deferred`, `blocked` = waiting on a named external dependency; `Waiting on:` never implies blocked. [detail](epic-log/decisions.md#d5) | user 2026-10-19 via agent_team manager (E4 showed Blocked vs `deferred`) | never |
| 2026-10-19 | superseded by E4 single writer | agent_team does not rewrite E4 | Superseded by E4 single writer: agent_team aligns to EPIC-3 doctrine; the E4 rewrite belongs to the poly-maker E3-3 thread; its earlier reshape is superseded. [detail](epic-log/decisions.md#d6) | agent_team manager 2026-10-19 | never |
| 2026-10-19 | superseded by EPIC-4 `Doctrine: <n>` | `Spine format: 2` extends format 1 | Superseded by EPIC-4 `Doctrine: <n>`: header `Spine format: <n>` (undeclared = 1); format 2 adds the human layer (Goal, serves, contributes, Done means). [detail](epic-log/decisions.md#d7) | Jordi 2026-10-19 | never |
| 2026-10-19 | superseded by L-14 (a poly-maker thread writes E4) | E4 single writer | Jordi's agent_team thread "E4 test in polymaker" (d14c8f2e) owns E4's content; EPIC-3 checks only E4's structure and format, never its intent. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Launch is the start order | Launching a persona from the console is the start order: `ready` before launch, `active` after; written where status is defined in the skill. [detail](epic-log/decisions.md#d9) | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Jordi talks to EPIC-3's manager directly | From now on EPIC-3 and spine-format questions come straight to this thread, not via the previous manager. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Scope split with EPIC-4 | EPIC-4 owns Goal, Serves, contributes, Done means and `Doctrine: <n>`; EPIC-3 keeps tree tools, EPIC codes, status words, conformance, the console picker. [detail](epic-log/decisions.md#d11) | Jordi 2026-10-19 via orchestrator | never |
| 2026-10-19 | accepted | Split write surfaces with EPIC-4 | While E3-2 runs, EPIC-4 writes SKILL.md and spine-model.md; EPIC-3 writes the scripts, global-block.md and spine-creation.md; one worker per file (L-10). [detail](epic-log/decisions.md#d12) | Jordi's merge order 2026-10-19; EPIC-4 handback 277d585 | EPIC-4 step 2 approved |
| 2026-10-19 | accepted | Living-tree rules (E3-2, release 2026.10.19.3) | E3-2 living-tree rules (release 2026.10.19.3): `Goal: EPIC-<n>` on every ask; done closes, replaced gets `Superseded by:`; 14 d stale; handover to EPIC-4 step 3. [detail](epic-log/decisions.md#d13) | E3-2 merge 61d7e03 | EPIC-4 doctrine changes a rule |
