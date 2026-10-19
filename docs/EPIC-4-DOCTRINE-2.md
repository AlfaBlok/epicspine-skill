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

## Serves

[EPIC-2 EpicSpine operating system](EPIC-2-OPERATING-SYSTEM.md) wants a repository's spines to be its living memory and the common ground for agents. Doctrine 2 makes that memory readable by humans and by the agent_team console, and it versions the doctrine so readers know which sections to expect.

## Definition Of Done

Done means (until step 2 makes `## Done means` a recognised heading, the outcomes sit here):

- [ ] E4-1 New epics are Doctrine 2 by default: `spine_new.py` writes `Doctrine: 2`, Goal, Serves and Done means, and adds a "contributes" sentence for the child in its parent's Spine Map; the commit check blocks a new spine without them. Released on main, tests green.
- [ ] E4-2 The doctrine is versioned and written down: `references/spine-model.md` defines Doctrine 1 (today's format, unchanged and still valid) and Doctrine 2 (extends 1), with the sections each one promises. `spines.py --json` returns `doctrine`, `goal`, `serves`, `done_means`, each child's `contributes`, and `missing_sections`. Jordi has approved the Doctrine 2 text.
- [ ] E4-3 agent_team reads it: the console Overview of a Doctrine 2 spine shows Goal, the Serves chain up to the root, the children with their contributes sentences, and Done means above the tickets, read from `spines.py --json`. Checked on a live spine with a screenshot.
- [ ] E4-4 The compliance test passes: a fresh poly-maker session, asked only "make Epic 4 compliant with the latest EpicSpine doctrine", brings poly-maker E4 to Doctrine 2 without further instructions, and the console shows the result.

## Current State

Owner: EPIC-4 delivery manager (to be launched from the epicspine-skill orchestrator thread)
Status: ready
Last attempted: 2026-10-19 EPIC-4 created by Jordi's decision; Doctrine 2 items moved here from EPIC-3
Result: spine written, no ticket started
Evidence: EPIC-2 Decisions 2026-10-19 "Doctrine ownership"
Waiting on: none
Approved work: E4-1 to E4-4 (Jordi, 2026-10-19)
Next action: write the Doctrine 2 text in references/spine-model.md and get Jordi's approval (step 1)
Source revision: main
Verified at: 2026-10-19

## Non-Goals

No change to Doctrine 1 spines: they stay valid and readable. No rename of existing headers. No E4 content written from here or from agent_team: poly-maker writes its own spines. Workflow style (`Spine dialect:` v1/v2) is a separate axis and stays.

## Issue Ledger

Steps run in this order; each one unblocks the next.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Delivery manager | EPIC-4 delivery manager | 1. Doctrine 2 text in spine-model.md (sections, Doctrine 1 vs 2 table, `Doctrine:` header, status words); Jordi approves | draft | none | none | main | none | 2026-10-19 | draft the text with a worker; show Jordi |
| draft | Ticket worker | worker (Sonnet 5.5) | 2. Tools: `spine_new` writes Doctrine 2 by default; `## Done means` accepted as the DoD heading; `spines --json` fields; commit check for new spines; template; release | draft | step 1, EPIC-3 E3-1 merged | none | main | EPIC-3 round 2 at 3bad60f (tools base) | 2026-10-19 | dispatch after step 1 |
| draft | agent_team delivery manager | agent_team thread | 3. Console reads Doctrine 2 from `spines --json` and shows Goal, Serves chain, children, Done means first | draft | step 2 | none | main | no console commits since 2026-10-18 | 2026-10-19 | hand the contract to agent_team after step 2 |
| draft | poly-maker delivery manager | fresh poly-maker thread | 4. Compliance test: "make Epic 4 compliant with the latest EpicSpine doctrine", nothing more; console shows it | draft | steps 2-3 | none | main | none | 2026-10-19 | launch a fresh thread in the poly-maker project |
| draft | Delivery manager | EPIC-4 delivery manager | 5. Make this repo's own spines (EPIC-2, EPIC-3) Doctrine 2 | draft | step 2 | none | main | EPIC-4 is the first Doctrine 2 spine | 2026-10-19 | after step 2 |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-19 | accepted | Roles | epicspine-skill owns the doctrine; agent_team complies when its console reads repos; each repo (e.g. poly-maker for its E4) applies the doctrine to its own spines in its own thread. Orchestrated from epicspine-skill. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | One version line: `Doctrine: <n>` | Replaces both proposals ("Spine format: n" and "Doctrine: <skill release>"). An integer: absent = 1. spine-model.md maps each number to its sections and to the skill release that introduced it. | Jordi asked for a recorded doctrine version; one line is enough | a third doctrine |
| 2026-10-19 | accepted | Doctrine 2 extends 1 | Jordi likes Doctrine 1. Doctrine 2 adds Goal (Mission still counts), Serves, a contributes sentence per child, Done means above the tickets, an `EPIC-<n>:` title and one status. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Start order | Launching a persona on a spine from the console is the start order; the persona carries the goal to completion. Status reads ready before the launch and active after it. | Jordi 2026-10-19 | never |
