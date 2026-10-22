# EPIC-4: Doctrine 2 semantic goal tree

Spine profile: compact
Ticket backend: github
Spine dialect: v1
Doctrine: 2
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-4-DOCTRINE-2.md
Spine ID: epicspine-doctrine-2
Spine Type: branch
Root spine: [EPIC-0 EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Parent spine: [EPIC-0 EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main

## Goal

Every spine says in plain words what it achieves and why, how it serves its parent, and what each of its children contributes, so a whole repo reads as one coherent story from root to leaf. Jordi and agent_team personas can then see at a glance what a goal means and when it is truly complete, not just which tickets are open.

The spine itself is the simple prototype: a spine is a snapshot of intent, facts and learnings, plus behaviours for maintenance and for dispatching workers. A cold agent given only the spine knows how to keep going, what the state is and where the issues are, then builds its own context as it needs it. A spine holds only what is specific to it; defaults live at repo or machine level.

## Serves

[EPIC-0 EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md) wants a repository's spines to be its living memory and the common ground for agents. Doctrine 2 makes that memory readable by humans and by the agent_team console, and it versions the doctrine so readers know which sections to expect.

## Definition Of Done

Done means (until step 2 makes `## Done means` a recognised heading, the outcomes sit here):

- [x] E4-1 New epics follow the doctrine by default: `spine_new.py` writes Goal, Serves and Done means, and adds a "contributes" sentence for the child in its parent's Spine Map; the commit check blocks a newly added epic without them (existing epics keep passing). Released on main, tests green.
- [x] E4-2 The doctrine is written down, unversioned: `references/spine-model.md` holds one current definition with the L-16 vocabulary (tree from EPIC-0; leaf = epic or page; only epics have required structure; intent or goal must be an epic; learning L-<n>; step = testable mid-outcome closed with evidence; unlinked = orphan). It is one short page a newcomer reads, replaces skill text rather than adding to it (net skill size does not grow), and everything it requires is enforced at the trackable level or dropped. `spines.py --json` returns `goal`, `serves`, `done_means`, each child's `contributes`, each epic's pages, orphan pages, and `missing_sections`. Jordi has approved the text.
- [x] E4-3 agent_team reads it: the console Overview of a Doctrine 2 spine shows Goal, the Serves chain up to the root, the children with their contributes sentences, and Done means above the tickets, read from `spines.py --json`. Checked on a live spine with a screenshot.
- [ ] E4-4 The compliance test passes: a fresh poly-maker session, asked only "make Epic 4 compliant with the latest EpicSpine doctrine", brings poly-maker E4 to Doctrine 2 without further instructions, and the console shows the result. Where poly-maker E4's "why" is not written anywhere in the repo, the agent asks Jordi rather than inventing one (one question about the why is a good result).
- [ ] E4-5 A fresh agent can pick up a spine cold: launched against a Doctrine 2 spine with no other brief, it states the goal, what done means, its next action and where its context lives, without asking. Tested on EPIC-4 itself and on poly-maker E4 after migration.

## Current State

Owner: EPIC-4 delivery manager (thread mcp:61d2777c-071a-4feb-93e3-4db440b5d6ac)
Status: active
Last attempted: 2026-10-22 E4-5 cold-start check on EPIC-4 (seat1, console run run_1d057709): partial, step 19 opened
Result: steps 1-4, 7-17 done; step 6 active (EPIC-4 slimmed, E4-5 re-run after step 19, then EPIC-0 and EPIC-3); E4-1, E4-2 and E4-3 met
Evidence: cold agent given only `Bound epic:` (read-only) found the state, pages and open ask without asking, and its checks agree with Current State; it did not state the goal or its next action, and bound Learnings in force: none; [step 19](doctrine/steps.md#step-19)
Waiting on: Jordi: EPIC-4-A2
Approved work: E4-1 to E4-5; steps 10-12 requested by Jordi via agent_team (2026-10-20/21)
Next action: dispatch step 19 (cold pickup reply) and step 18 (worktree hook tests); on EPIC-4-A2, launch step 5
Source revision: main
Verified at: 2026-10-22 (main 234c4f6; spines.py 0 orphans 0 mismatches)


## Waiting on

- [ask EPIC-4-A2: approve @Jordi since 2026-10-22 row 5] Launch step 5 (the poly-maker E4 compliance test) now, although poly-maker E4's owner is actively working it (b0d6dd36)? — recommend: yes; warn the E4 owner first that a structure-only migration commit is coming — unblocks: step 5 (E4-4), then the E4-5 check on poly-maker E4 — effort: ~1 min — context: [poly-maker E4 activity](https://github.com/AlfaBlok/poly-maker/commit/b0d6dd36) (console item nj_4dcdbafa)
- [answered EPIC-4-A1 2026-10-21 @Jordi] Approve the doctrine page (what every epic must say) and the enforcement plan (scaffold, commit check, JSON fields) as one? — recommend: approve, with both small answers yes (advisory size budget 150 lines / 200-char cells; profile, dialect and ticket-backend headers optional) — unblocks: step 3 (tools), then 5 (poly-maker compliance test) and 6 (slimming); waiting holds the whole Doctrine 2 rollout — effort: ~5 min — context: [approval page](http://vps-a9-1.taild81fbb.ts.net:36879/index.html) — answer: APPROVED

## Non-Goals

No change to Doctrine 1 spines: they stay valid and readable. No rename of existing headers. No E4 content written from here or from agent_team: poly-maker writes its own spines. Workflow style (`Spine dialect:` v1/v2) is a separate axis and stays.

## Issue Ledger

Steps run in this order; each one unblocks the next. Steps 1 and 2 are one approval (doctrine page + [enforcement plan](doctrine/enforcement.md)); step 4 runs in parallel with step 3 against the [console contract](doctrine/console-contract.md). Step 7 runs as soon as step 1's vocabulary is approved, before step 6, so the repo migrates once.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Delivery manager | worker seat1 (Sonnet 5.5), task epic4-step1-doctrine-draft-r1 | 1. Define the doctrine (coherence pass): one short page that replaces skill text; Jordi approves. [detail](doctrine/steps.md#step-1) | done | none | merged | main | merged 9f3b093 (wt/doctrine-2 0fabf2d); approved EPIC-4-A1; doc/spine tests OK; SKILL.md 79->72 lines | 2026-10-22 | none |
| draft | Delivery manager | EPIC-4 delivery manager | 2. Plan enforcement: scaffold, commit check, `spines --json` visibility, size budget, migration; Jordi approves before tool work. [detail](doctrine/steps.md#step-2) | done | step 1 | none | main | [enforcement.md](doctrine/enforcement.md) on main; approved EPIC-4-A1 2026-10-21 | 2026-10-22 | none; built by step 3 |
| draft | Ticket worker | worker seat1 (Sonnet 5.5), task epic4-step3-tools-r1, console run run_4b6bd75d | 3. Tools: `spine_new` writes Doctrine 2, `## Done means`, `spines --json` fields, commit check, template, release. [detail](doctrine/steps.md#step-3) | done | step 2 (done) | merged | main | released 2026.10.22.1 (merge 6be5e7c); full isolated suite 606 OK (2 skip); skill -3 lines | 2026-10-22 | none |
| draft | agent_team delivery manager | agent_team thread mcp:6734cbcd-4cab-456a-9bcc-dbff1b10f713 | 4. Console reads Doctrine 2 from `spines --json` (Goal, Serves chain, children, Done means); verify the persona pipeline. [detail](doctrine/steps.md#step-4) | done | contract (parallel with step 3); live check after step 3 | none | main | live check on 2026.10.22.1 (2026-10-22): Definitions tab shows Goal, Serves chain, Done means; EPIC-0 children + contributes; agent_team 1a27502, ca8fc10, c5f8bdb; E4-3 met | 2026-10-19 | relink orphan page tools-brief.md at the step 6 merge |
| draft | poly-maker delivery manager | fresh poly-maker thread | 5. Compliance test on poly-maker E4 ("make Epic 4 compliant with the latest EpicSpine doctrine"), then the E4-5 cold-start check there. [detail](doctrine/steps.md#step-5) | draft | step 3 shipped and skill synced to vps1 (launch); step 4 (console view) | none | main | none | 2026-10-19 | launch a fresh thread in the poly-maker project (2026.10.22.1 released) |
| draft | Delivery manager | EPIC-4 delivery manager | 6. Slim to L-17, EPIC-4 first, then the E4-5 cold-start check on it; then EPIC-0 (root) and EPIC-3. [detail](doctrine/steps.md#step-6) | active | step 3 | merged | main | EPIC-4 slimmed: merge d0e138a (wt/epic4-slim 1ea86b2, branch removed): long_cells 24 -> 0, detail in [steps.md](doctrine/steps.md) and [decisions.md](doctrine/decisions.md), docs tests OK; E4-5 cold check on EPIC-4 partial (see step 19) | 2026-10-22 | after step 19, re-run E4-5 on EPIC-4; then EPIC-0 and EPIC-3 |
| draft | Ticket worker | worker seat1 (Sonnet 5.5), task epic4-step7-root-swap-r1 | 7. Root swap (L-15): EPIC-2 root becomes EPIC-0, done audit EPIC-0 becomes EPIC-2; rename files, update links repo-wide. [detail](doctrine/steps.md#step-7) | done | step 1 vocabulary approved (L-16, done) | wt/root-swap | main | merged and pushed: main ef15cfa (branch 336ae54); doc-reading tests pass; briefs updated by root DM (719ffe9) | 2026-10-19 | none; see step 8 for the load-failing sync tests |
| draft | Delivery manager | EPIC-4 delivery manager | 8. Quiet re-run of 4 sync tests that failed under load 34 (pre-commit in a linked worktree runs main's hook). [detail](doctrine/steps.md#step-8) | done | quiet host | none | main | 2026-10-22 load 1.8: background_sync 55, session_sync 61, local_mess 33, auto_return 23, all OK; hook finding moved to step 18 | 2026-10-22 | none |
| draft | Ticket worker | native subagent (Sonnet 5.5), resumed after seat1 provider failure | 9. Personas must receive the doctrine: tests never touch real harness config; installer never targets a worktree. [detail](doctrine/steps.md#step-9) | done | none | merged | main | released 2026.10.21.2 (merge 383ac11); isolated suite 562 OK; seat1 found stripped again 2026-10-21 (pre-fix runs) and reinstalled from main; seat2 and ~/.claude current | 2026-10-19 | agent_team repeats the fresh persona launch |
| draft | Ticket worker | worker (wt/outcome) | 10. Outcome before close: every closed spine has `## Outcome`; gate blocks a done spine without it; `outcome` in `--json`. [detail](doctrine/steps.md#step-10) | done | none (independent of steps 1-3) | wt/outcome | main (branch removed) | released 2026.10.20.2 (21adcba); test_outcome OK; `outcome` in --json; full suite 532 OK (1 skip); release + JSON sent to agent_team | 2026-10-21 | none; agent_team backfills Outcome on m3-reddit-search, m4-browser-auth-sync |
| draft | Ticket worker | worker (wt/outcome, same release as step 10) | 11. Current State for the console: `current_state` per node in `--json`; manager updates it every session or wake. [detail](doctrine/steps.md#step-11) | done | none | wt/outcome | main (branch removed) | released 2026.10.20.2 (21adcba); `current_state` in --json; full suite 532 OK (1 skip); release + JSON sent to agent_team | 2026-10-21 | none |
| draft | Ticket worker | worker (Sonnet 5.5) | 12. Human asks: structured `## Waiting on` lines, answer write-back, `waiting_on` in `--json`, advisory checks. [detail](doctrine/steps.md#step-12) | done | none | wt/human-asks | main | released 2026.10.21.1 (merge 5672974); full isolated suite 554 OK; EPIC-4 waiting_on shows the open ask | 2026-10-21 | agent_team M2-13 reads `waiting_on` |
| draft | Ticket worker | worker (Sonnet 5.5) | 13. `sync_schedule.py` takes its path from `__file__`; route the cron entry through install_guard. [detail](doctrine/steps.md#step-13) | done | none | none | main | released 2026.10.21.3 (merge 91011ec); isolated suite OK; real cron names the main checkout | 2026-10-21 | none |
| draft | Ticket worker | worker (Sonnet 5.5) | 14. Learnings in force = the bound epic's plus every ancestor's up to the root; one wording fix in global-block rule 1/2. [detail](doctrine/steps.md#step-14) | done | none | none | main | released 2026.10.21.4 (merge b1033ff); isolated suite 566 OK | 2026-10-21 | none |
| draft | Ticket worker | worker (Sonnet 5.5) | 15. `current_state` adds Owner and Approved work (human-asks answers route via `current_state.owner`). [detail](doctrine/steps.md#step-15) | done | none | merged | main | released 2026.10.21.5; isolated suite 566 OK; EPIC-4 current_state.owner names this thread | 2026-10-21 | none |
| draft | Ticket worker | worker seat2 (Sonnet 5.5) | 16. Worker briefs name the bound epic so workers walk the parent chain for learnings. [detail](doctrine/steps.md#step-16) | done | none | merged | main | released 2026.10.21.6; isolated suite OK; the step 16 worker itself bound with L-1..L-14 from EPIC-0 | 2026-10-21 | none |
| draft | Ticket worker | worker (Sonnet 5.5) | 17. Human asks v2: ask codes, `do` + steps, unblocks/effort, gate is not an ask, answer by code. [detail](doctrine/steps.md#step-17) | done | none | merged | main | released 2026.10.21.7 (merge 2788fcf); full isolated suite OK; EPIC-4-A1 parses with code, unblocks, effort | 2026-10-21 | poly-maker E4 owner restates its gates as v2 asks |
| draft | Ticket worker | unassigned | 18. Pre-commit tests run from a linked worktree exercise main's installed hook, not the branch's code (found by the step 3 worker, who ran from a plain clone). [detail](doctrine/steps.md#step-18) | draft | none | none | main | step 3 report 2026-10-22 | 2026-10-22 | dispatch a test fix (resolve the hook from the tested checkout) |
| draft | Ticket worker | unassigned | 19. Cold pickup reply: an agent given only `Bound epic:` audited the epic instead of stating goal, Done means, next action and where context lives, and bound Learnings in force: none. [detail](doctrine/steps.md#step-19) | draft | none | none | main | cold check 2026-10-22 (console run run_1d057709) | 2026-10-22 | brief a skill fix, then re-run E4-5 on EPIC-4 |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-19 | accepted | Roles [detail](doctrine/decisions.md#d1) | epicspine-skill owns the doctrine; agent_team and each repo comply and apply it to their own spines in their own threads. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | One version line: `Doctrine: <n>` [detail](doctrine/decisions.md#d2) | `Doctrine: <n>` is an integer (absent = 1); it replaces both earlier proposals. | Jordi asked for a recorded doctrine version; one line is enough | a third doctrine |
| 2026-10-19 | accepted | Doctrine 2 extends 1 [detail](doctrine/decisions.md#d3) | Adds Goal, Serves, a contributes sentence per child, Done means above the tickets, an `EPIC-<n>:` title and one status. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Start order [detail](doctrine/decisions.md#d4) | Launching a persona on a spine from the console is the start order; status reads ready before the launch, active after. | Jordi 2026-10-19 | never |
| 2026-10-19 | accepted | Define, then plan, then build [detail](doctrine/decisions.md#d5) | Step 1 defines the doctrine, step 2 plans enforcement for Jordi's approval before any tool work; former steps 2-5 became 3-6. | Jordi via orchestrator 2026-10-19 | never |
| 2026-10-19 | accepted | A fresh agent must know what to do [detail](doctrine/decisions.md#d6) | Added E4-5 (cold-start test); an unwritten why is asked of the owner, never invented; step 4 verifies personas bind. | Jordi via orchestrator 2026-10-19 | after Jordi answers the How to work this question |
| 2026-10-19 | accepted | Step 1 is a coherence pass [detail](doctrine/decisions.md#d7) | vps1 scan found five version-like switches and `--strict` failing on 14 of 23 spines; Doctrine 2 becomes one page that replaces text; (b)-(f) go to Jordi one at a time. | orchestrator vps1 scan 2026-10-19 | after Jordi answers (b)-(f) |
| 2026-10-19 | accepted | File handoff with EPIC-3 [detail](doctrine/decisions.md#d8) | EPIC-4 hands the EPIC-3 files back for E3-2; step 3 claims them afterwards; the doctrine page is drafted after round 3 merges. | EPIC-3 manager handoff 2026-10-19 | step 2 approved |
| 2026-10-20 | accepted | Outcome contract in snake_case [detail](doctrine/decisions.md#d9) | The contract uses snake_case (`done_means`, `closed_at`, `closed_by`) like every other `--json` field; step 10 runs ahead of steps 1-3. | EPIC-4 manager 2026-10-20 | agent_team objects |
| 2026-10-20 | accepted | `current_state` keys follow the field labels [detail](doctrine/decisions.md#d10) | Each key is the snake_case form of its Current State label (`last` becomes `last_attempted`); `evidence` is added. | EPIC-4 manager 2026-10-20 | agent_team objects |
| 2026-10-19 | accepted | No "How to work this" section; the spine is the prototype [detail](doctrine/decisions.md#d11) | Jordi: a spine is a snapshot of intent, facts and learnings plus behaviours; no generic how-to section; tested by E4-5; supersedes the (a) recommendation in D6. | Jordi via orchestrator 2026-10-19 | never |
| 2026-10-19 | accepted | Root is EPIC-0; one migration [detail](doctrine/decisions.md#d12) | L-15: the root spine is always EPIC-0; the EPIC-2/EPIC-0 swap is one worker job (step 7), after the vocabulary is settled. | EPIC-0 L-15 (23f9f30) | never |
| 2026-10-19 | accepted | Vocabulary and versioning [detail](doctrine/decisions.md#d13) | L-16: the tree hangs from EPIC-0; a leaf is an epic or a page; learnings are L-<n>; a step is a testable mid-outcome closed with evidence; unlinked = orphan. | EPIC-0 L-16 (fe94053, 5030649) | never |
| 2026-10-19 | accepted | L-16 tree shape [detail](doctrine/decisions.md#d14) | L-16 refined: any leaf may have children at any depth; an epic has one parent, a page one or more; status rolls up to the nearest epic ancestor. | Jordi via orchestrator 2026-10-19 | never |
| 2026-10-19 | accepted | L-17 tidy, minimal epics [detail](doctrine/decisions.md#d15) | Answers (d): keep the epic informed after each step, propagate major findings upward, one-line Decisions linking to pages, advisory size budget; EPIC-4 is slimmed first (step 6). | EPIC-0 L-17 (root swap commit) | never |
| 2026-10-19 | accepted | Compress to the console [detail](doctrine/decisions.md#d16) | Doctrine page and enforcement plan go to Jordi as one approval; the console contract goes to agent_team now; L-15..L-17 become skill doctrine. | Jordi via orchestrator 2026-10-19 | never |
| 2026-10-19 | accepted | Personas lost the doctrine [detail](doctrine/decisions.md#d17) | Tests leaking CLAUDE_CONFIG_DIR and `__file__`-based installer paths broke seat1 hooks; fixed as step 9, blocks the E4-3 pipeline check. | agent_team pipeline check 2026-10-19 | step 9 merged |
| 2026-10-21 | accepted | EPIC-4-A1: doctrine page and enforcement plan [detail](doctrine/decisions.md#d18) | APPROVED as one, both small answers yes (advisory budget 150 lines / 200-char cells; profile, dialect, ticket-backend headers optional); unblocks step 3, then 5 and 6. | Jordi via agent_team console (item wj_7f4157f90d7b8a48), EPIC-4-A1 | never |
