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
Last attempted: 2026-10-22 re-oriented after EPIC-4 closed (340333f); E3-4 verified live; conformance rescan of 16 repos ([scan](epic-log/conformance.md)); spines.py speed step dispatched; poly-maker and infra-vps migrations launched; poly-maker green (verified), zenod launched
Result: E3-4 met (picker lists poly-maker EPIC-4 via spines.py). Cold spines.py on poly-maker takes 10-23 s under load against the console's 15 s timeout; parsing, not the walk, is the cost, and the console already answers from its last good result (agent_team spines.ts:290), so only a cold start falls back; 2026.10.22.6 (83b4b9b) trims CPU and stops a git timeout crashing the scan. E3-2 has 1 of 3 live proofs
Evidence: [conformance scan 2026-10-22](epic-log/conformance.md)
Waiting on: EPIC-3-A1
Approved work: E3-1 to E3-5 (user, 2026-10-19)
Next action: take reports from infra-vps (mcp:51557bfc) and zenod (mcp:aa9a971f), then launch tax-assist-research and abnb-agent
Source revision: main @ 21e3892
Verified at: 2026-10-22

## Mission

Goal: every goal in every repo is an EPIC with a code, a one-line goal and success criteria, hung in one tree from the repo's root, and agents keep that tree true.

Why: Jordi and the agent_team console must see what is open, settled and archived, and attach personas to active goals. "All repos on latest" was said while goal docs (poly-maker E4) sat outside any tree.

## Serves

[EPIC-0 EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md) wants a repository's spines to form one tree of goals, each stating its purpose and measurably accomplishable (EPIC-0 Mission). This epic makes that true: every goal is a coded EPIC in one tree per repo, kept true by agents (EPIC-0 Spine Map).

## Waiting on

- [ask EPIC-3-A1: decide @Jordi since 2026-10-22 row E3-3] Give a root spine to the six repos that have none (idea_scraper, obsidian-brain, zenod-cloud, nectary, zenod_memory, alpha9_webflow_export)? — options: all | none | pick — recommend: idea_scraper, obsidian-brain, zenod-cloud (active goals live there); none for the other three, recorded as exceptions — unblocks: E3-3 for those repos; nothing else waits — effort: ~1 min — context: [scan](epic-log/conformance.md)

## Non-Goals

No rename of existing files or header fields. Migration changes structure only (header, links, state, checkboxes), never what a goal means. No cross-repo portfolio root yet. agent_team console code is agent_team's work; this epic delivers the contract it reads.

## Definition Of Done

- [x] E3-1 The skill ships it: the definition, `spine_new.py`, `spines.py --json` and the commit check are released on main with tests green.
- [ ] E3-2 Agents keep it true: every new ask is answered with a `Goal: EPIC-<n>` line and lands in the tree; done or replaced goals close; goals active but untouched 14 days are flagged. Measured by tests plus 3 fresh sessions in different repos.
- [ ] E3-3 Every repo conforms: `spines.py --json` on each repo on vps1 shows 0 orphans and 0 mismatches, or each exception is recorded in that repo; repos without a root were offered one and the answer is recorded. Proof: a published before/after table.
- [x] E3-4 The console sees it: the agent_team milestone picker lists poly-maker E4, read from `spines.py --json`.
- [ ] E3-5 "On latest EpicSpine" means installed and conforming (E3-3 green): an Operating Learning in EPIC-0, and no current instruction says otherwise.

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker (Sonnet 5.5, seat pool) | E3-1 skill tools: definition, `spine_new`, tree gate, `spines --json`; release 2026.10.19.1 | done | none | none | main | r1+r2+r3 merged (cab199a, 4639aa9, 88f00fa, 52cdd31..20b4602), release 2026.10.19.2; 508 tests, url_gate flakes only under host load | 2026-10-19 | none |
| draft | Ticket worker | worker (Sonnet 5.5) | E3-2 living tree: `Goal: EPIC-<n>`, Record duties, `--active`, 14 d stale, codes from `spine_new` [detail](epic-log/steps.md#ticket-2) | active | E3-1 | none | main | merged 61d7e03 (2026.10.19.3); live proof 1/3: poly-maker e25fa5ad answered `Goal: EPIC-4` unprompted (2026-10-22) | 2026-10-22 | proofs 2-3 from the infra-vps and zenod migration threads (plain ask, no goal named) |
| draft | Repo delivery manager | poly-maker thread mcp:aac4e0e3 | E3-3 migrate poly-maker: 3 orphans (analysis/*/SPINE.md), 14 looks_like_epic; E4 content untouched [detail](epic-log/steps.md#ticket-3) | done | E3-1 | main-direct | main | verified 2026-10-22: 58 nodes, 0 orphans, 0 mismatches, 14 pages recorded as exceptions (poly-maker 1dc21c66..69a3a0d8) | 2026-10-22 | none |
| draft | Repo delivery manager | per-repo threads | E3-3 migrate infra-vps (39 looks_like_epic, thread mcp:51557bfc), zenod (28, thread mcp:aa9a971f), tax-assist-research (4 mismatches), abnb-agent (4); rootless repos per EPIC-3-A1 | active | E3-1 | main-direct | main | [scan 2026-10-22](epic-log/conformance.md) | 2026-10-22 | tax-assist-research + abnb-agent after infra-vps reports |
| draft | Delivery manager | EPIC-3 delivery manager | E3-3 conformance table, before/after per repo | active | E3-3 migrations | none | main | before column: [scan 2026-10-22](epic-log/conformance.md) | 2026-10-22 | after column when migrations land |
| draft | Repo delivery manager | agent_team | E3-4 console picker reads `spines.py --json` | done | E3-1 | none | main | 2026-10-22 live: `/api/repos/poly-maker/docs` lists `EPIC-4: ONE LOGGER` via `spines`, parent EPIC0.md (agent_team 9e53c7d); [screenshot](doctrine/evidence/polymaker-e4-done-means-2026-10-22.png) | 2026-10-22 | none |
| draft | Ticket worker | worker (Sonnet 5.5, seat1/seat2) | spines.py under load: read each file once; stale check survives git timeouts (risk from EPIC-4: cold run vs console 15 s timeout) | done | none | merged | main | merged 83b4b9b (2026.10.22.6): ~15% less CPU, output byte-identical on poly-maker/zenod; isolated suite 625 OK; console last-good cache covers the rest | 2026-10-22 | none |
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
| 2026-10-22 | accepted | E3-3 bar under Doctrine 2 | Green = 0 `orphans`, 0 `mismatches`, and each `looks_like_epic` page made a coded epic or kept as a linked page / recorded exception; `orphan_pages` is advisory (spine-model.md), reported, not chased. | spine-model.md "Page and orphan checks are advisory" | doctrine makes pages blocking |
| 2026-10-22 | accepted | spines.py speed is an EPIC-3 step | EPIC-4's open risk (cold spines.py vs the console's 15 s timeout) moves here with the scripts (EPIC-4 closed); measured 19-23 s, so it gets a step, not a watch. | 2026-10-22 timing on poly-maker | never |
| 2026-10-22 | accepted | spines.py timeout risk: mitigate, don't chase | The console's last-good cache covers slow scans; the skill only trims CPU (~15%) and makes the stale check timeout-safe. The git ls-files listing was dropped (no wall gain, L-1). | wt/spines-fast r1 report; agent_team spines.ts:290 | a cold-start fallback is seen in the console |
