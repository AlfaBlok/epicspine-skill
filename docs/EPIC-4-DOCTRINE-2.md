# EPIC-4: Doctrine 2 semantic goal tree

Spine profile: compact
Ticket backend: github
Spine dialect: v1
Doctrine: 2
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-4-DOCTRINE-2.md
Spine ID: epicspine-doctrine-2
Spine Type: branch
Root spine: [EPIC-2 EpicSpine operating system](EPIC-2-OPERATING-SYSTEM.md)
Parent spine: [EPIC-2 EpicSpine operating system](EPIC-2-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main

## Goal

Every spine says in plain words what it achieves and why, how it serves its parent, and what each of its children contributes, so a whole repo reads as one coherent story from root to leaf. Jordi and agent_team personas can then see at a glance what a goal means and when it is truly complete, not just which tickets are open.

The spine itself is the simple prototype: a spine is a snapshot of intent, facts and learnings, plus behaviours for maintenance and for dispatching workers. A cold agent given only the spine knows how to keep going, what the state is and where the issues are, then builds its own context as it needs it. A spine holds only what is specific to it; defaults live at repo or machine level.

## Serves

[EPIC-2 EpicSpine operating system](EPIC-2-OPERATING-SYSTEM.md) wants a repository's spines to be its living memory and the common ground for agents. Doctrine 2 makes that memory readable by humans and by the agent_team console, and it versions the doctrine so readers know which sections to expect.

## Definition Of Done

Done means (until step 2 makes `## Done means` a recognised heading, the outcomes sit here):

- [ ] E4-1 New epics are Doctrine 2 by default: `spine_new.py` writes `Doctrine: 2`, Goal, Serves and Done means, and adds a "contributes" sentence for the child in its parent's Spine Map; the commit check blocks a new spine without them. Released on main, tests green.
- [ ] E4-2 The doctrine is versioned and written down: `references/spine-model.md` defines Doctrine 1 (today's format, unchanged and still valid) and Doctrine 2 (extends 1), with the sections each one promises. `spines.py --json` returns `doctrine`, `goal`, `serves`, `done_means`, each child's `contributes`, and `missing_sections`. The Doctrine 2 text is one short page a newcomer reads, replaces skill text rather than adding to it (net skill size does not grow), and everything it requires is enforced at the trackable level or dropped. Jordi has approved the Doctrine 2 text.
- [ ] E4-3 agent_team reads it: the console Overview of a Doctrine 2 spine shows Goal, the Serves chain up to the root, the children with their contributes sentences, and Done means above the tickets, read from `spines.py --json`. Checked on a live spine with a screenshot.
- [ ] E4-4 The compliance test passes: a fresh poly-maker session, asked only "make Epic 4 compliant with the latest EpicSpine doctrine", brings poly-maker E4 to Doctrine 2 without further instructions, and the console shows the result. Where poly-maker E4's "why" is not written anywhere in the repo, the agent asks Jordi rather than inventing one (one question about the why is a good result).
- [ ] E4-5 A fresh agent can pick up a spine cold: launched against a Doctrine 2 spine with no other brief, it states the goal, what done means, its next action and where its context lives, without asking. Tested on EPIC-4 itself and on poly-maker E4 after migration.

## Current State

Owner: EPIC-4 delivery manager (thread mcp:61d2777c-071a-4feb-93e3-4db440b5d6ac)
Status: active
Last attempted: 2026-10-19 Jordi: root is always EPIC-0 (L-15, swap planned as step 7); (b) reopened as a vocabulary proposal, versioning in question; draft holds both
Result: spine re-staged, no ticket started
Evidence: EPIC-2 Decisions 2026-10-19 "Doctrine ownership"; Decisions 2026-10-19 "Define, then plan, then build", "A fresh agent must know what to do", "Step 1 is a coherence pass"
Waiting on: none
Approved work: E4-1 to E4-4 (Jordi, 2026-10-19); E4-5 added from Jordi's questions (2026-10-19)
Next action: verify the worker's draft on wt/doctrine-2 (lines must not grow; versioning and vocabulary held); Jordi is deciding the vocabulary and whether to version at all; then (c)-(f) one at a time (step 1)
Source revision: main
Verified at: 2026-10-19

## Non-Goals

No change to Doctrine 1 spines: they stay valid and readable. No rename of existing headers. No E4 content written from here or from agent_team: poly-maker writes its own spines. Workflow style (`Spine dialect:` v1/v2) is a separate axis and stays.

## Issue Ledger

Steps run in this order; each one unblocks the next. Steps 1 and 2 are approval gates: no tool work before Jordi approves both. Step 7 runs as soon as step 1's vocabulary is approved, before step 6, so the repo migrates once.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Delivery manager | worker seat1 (Sonnet 5.5), task epic4-step1-doctrine-draft-r1 | 1. Define the doctrine (coherence pass): one short page a newcomer reads, replacing skill text, not adding to it; Doctrine 2 text in plain language (what a spine must say, and why; Doctrine 1 vs 2 table; `Doctrine:` header; status words; rule: if a goal's why is not written in the repo, ask the spine's owner, never invent it) plus open ambiguities as concrete questions, one at a time, each with a recommendation, in this order (a, How to work this, dropped by Jordi: the cold-start objective is in the Goal and E4-5): (b) One switch: `Doctrine: <n>` is what a reader needs; profile and dialect become optional, one line each; `leaf` accepted as alias of `branch`. (c) Spine vs tickets: the ledger row is the ticket; a GitHub issue or local ticket file is optional, linked only when one step needs its own discussion; one concrete what-goes-where example. (d) Maintenance duties in at most 5 lines (record, close, roll up to parent, supersede, keep Current State lean), mechanics owned by EPIC-3 E3-2. (e) Glossary of at most 6 lines (Goal/Mission, Done means/DoD/Acceptance, epic/spine/goal/milestone). (f) `--strict` stays advisory; whatever Doctrine 2 requires is enforced at the trackable level or dropped. Jordi approves | active | none | wt/doctrine-2 | main | EPIC-3 round 3 merged be51d42; draft dispatched 2026-10-19; (a) dropped, (b) put to Jordi | 2026-10-19 | round 3 merged (be51d42): worker drafts the page on top of it, held on a branch until Jordi approves; ask (b)-(f) one by one; coordinate (d) with EPIC-3's manager |
| draft | Delivery manager | EPIC-4 delivery manager | 2. Plan enforcement: short plan for Jordi covering scaffold (new spines Doctrine 2 by default), commit check (violations caught), version visibility (`spines --json`, console), migration ("make it compliant" path); Jordi approves before any tool work | draft | step 1 | none | main | none | 2026-10-19 | write the plan after step 1 is approved |
| draft | Ticket worker | worker (Sonnet 5.5) | 3. Tools: `spine_new` writes Doctrine 2 by default; `## Done means` accepted as the DoD heading; `spines --json` fields; commit check for new spines; template; release | draft | step 2; tool files free of EPIC-3 workers | none | main | E3-1 r1+r2 merged (cab199a, 4639aa9; main af76226, 507 tests OK); spines.py at its 200-line budget | 2026-10-19 | after step 2 is approved, claim spines.py/spine_new.py/pre_commit.py from EPIC-3's manager (E3-2 may hold them) and dispatch |
| draft | agent_team delivery manager | agent_team thread | 4. Console reads Doctrine 2 from `spines --json` and shows Goal, Serves chain, children, Done means first; also verify the agent pipeline: a persona launched from the console receives the EpicSpine always-on block (SessionStart hook) and binds to its spine | draft | step 3 | none | main | no console commits since 2026-10-18 | 2026-10-19 | hand the contract (incl. the pipeline check) to agent_team after step 3 |
| draft | poly-maker delivery manager | fresh poly-maker thread | 5. Compliance test: "make Epic 4 compliant with the latest EpicSpine doctrine", nothing more; console shows it; success includes asking Jordi for any unwritten why; then run the E4-5 cold-start check on poly-maker E4 | draft | step 3 shipped and skill synced to vps1 (launch); step 4 (console view) | none | main | none | 2026-10-19 | launch a fresh thread in the poly-maker project once step 3 is on vps1 |
| draft | Delivery manager | EPIC-4 delivery manager | 6. Make this repo's own spines (EPIC-2, EPIC-3) Doctrine 2; run the E4-5 cold-start check on EPIC-4 | draft | step 3 | none | main | EPIC-4 is the first Doctrine 2 spine | 2026-10-19 | after step 3 |
| draft | Ticket worker | worker (Sonnet 5.5) | 7. Root swap (L-15): EPIC-2 root becomes EPIC-0, done audit EPIC-0 becomes EPIC-2; one job: rename files, update links and headers repo-wide (docs, README, AGENTS.md `Root spine:`, examples, handoffs, explainer), and the live thread briefs that cite "EPIC-2 L-x"; history text left as is | draft | step 1 vocabulary approved; no EPIC-3 worker editing spine files at that moment | none | main | L-15 (23f9f30); 9 md files reference the root or EPIC-0 | 2026-10-19 | dispatch once Jordi settles the vocabulary, so the repo migrates once |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-19 | accepted | Roles | epicspine-skill owns the doctrine; agent_team complies when its console reads repos; each repo (e.g. poly-maker for its E4) applies the doctrine to its own spines in its own thread. Orchestrated from epicspine-skill. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | One version line: `Doctrine: <n>` | Replaces both proposals ("Spine format: n" and "Doctrine: <skill release>"). An integer: absent = 1. spine-model.md maps each number to its sections and to the skill release that introduced it. | Jordi asked for a recorded doctrine version; one line is enough | a third doctrine |
| 2026-10-19 | accepted | Doctrine 2 extends 1 | Jordi likes Doctrine 1. Doctrine 2 adds Goal (Mission still counts), Serves, a contributes sentence per child, Done means above the tickets, an `EPIC-<n>:` title and one status. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Start order | Launching a persona on a spine from the console is the start order; the persona carries the goal to completion. Status reads ready before the launch and active after it. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Define, then plan, then build | Jordi is not yet sure the doctrine is clear. Step 1 defines it in plain language and resolves ambiguities one question at a time; step 2 is an enforcement plan (scaffold, commit check, version visibility, migration) he approves before any tool work. Former steps 2-5 became 3-6. | Jordi via orchestrator 2026-10-19 | never |
| 2026-10-19 | accepted | A fresh agent must know what to do | Jordi asked whether a persona launched against a spine knows what is expected and where to look; today only partly (Next action, Approved work). Added E4-5 (cold-start test on EPIC-4 and poly-maker E4); step 1 puts a `## How to work this` section to Jordi as an open question, recommended yes; the doctrine says an unwritten why is asked of the owner, never invented; step 4 verifies console personas get the always-on block and bind. poly-maker's ad hoc "How to work this epic" note is the precedent. | Jordi via orchestrator 2026-10-19 | after Jordi answers the How to work this question |
| 2026-10-19 | accepted | Step 1 is a coherence pass | Jordi asked whether EpicSpine is self-consistent and clear; orchestrator says not yet. vps1 scan 2026-10-19: five version-like switches (profile compact 19/full 1, dialect v1 20/v2 4, backend github 11/local 5, Spine Type with 5 `leaf` the validator rejects, Doctrine); this repo declares github tickets but all 31 ledger rows are Issue `draft`, so `--strict` fails here and on 14 of 23 vps1 spines; maintenance duties partial (root Current State was thousands of chars, 15 flat goals); vocabulary drift; ~2,000 lines of skill text against L-1. Doctrine 2 becomes one short page that replaces text; open items (b)-(f) go to Jordi one at a time, each with a recommendation; required = enforced or dropped. | orchestrator vps1 scan 2026-10-19 | after Jordi answers (b)-(f) |
| 2026-10-19 | accepted | File handoff with EPIC-3 | E3-1 merged; EPIC-3 released spines.py, spine_new.py and pre_commit.py. EPIC-4 cannot touch them before step 2 is approved, so it hands them straight back for E3-2 rather than idling them; step 3 claims them afterwards and builds on E3-2. Step 1 overlaps round 3 (status words, `EPIC-<n>:` rule in spine-model.md), so the doctrine page is drafted only after round 3 merges and takes its wording as given. | EPIC-3 manager handoff 2026-10-19 | step 2 approved |
| 2026-10-19 | accepted | No "How to work this" section; the spine is the prototype | Jordi: a spine is "a snapshot of intent and facts and learnings, plus behaviours for maintenance and for dispatching workers". A generic how-to section confused him; defaults belong at repo or machine level and a spine holds only what is specific to it. His objective: a fresh agent reads the spine alone, knows how to keep going, the state and where the issues are, and builds its own context as needed. Written into the Goal; tested by E4-5. Supersedes the (a) recommendation in "A fresh agent must know what to do". | Jordi via orchestrator 2026-10-19 | never |
| 2026-10-19 | accepted | Root is EPIC-0; one migration | L-15: the root spine is always EPIC-0. This repo swaps EPIC-2 (root) and EPIC-0 (done audit) as one worker job (step 7), run after the vocabulary is settled so files, headers, links, AGENTS.md and thread briefs migrate once. | EPIC-2 L-15 (23f9f30) | never |
| 2026-10-19 | pending | Vocabulary and versioning | Jordi did not answer (b); he asked for an exact vocabulary and doubts a doctrine version is needed. Orchestrator proposes: root (EPIC-0), spine (any goal EPIC-n), step (ledger row or checkbox), page (supporting doc outside the tree), learning (one line); drop branch, leaf and `Spine Type:` (root = no parent); no `Doctrine: <n>` line, one current definition and the checker reports missing sections. The draft holds both parts; E4-1/E4-2 wording on versions follows his answer. | Jordi via orchestrator 2026-10-19 | Jordi answers |
