# Decisions of EPIC-4: detail

Page of [EPIC-4](../EPIC-4-DOCTRINE-2.md). The Decisions table there keeps one line per decision; the full Durable Summary of each, as it stood in the table, is here.

## D1

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Roles
- **Durable Summary:** epicspine-skill owns the doctrine; agent_team complies when its console reads repos; each repo (e.g. poly-maker for its E4) applies the doctrine to its own spines in its own thread. Orchestrated from epicspine-skill.
- **Evidence:** Jordi 2026-10-19
- **Revisit When:** never

## D2

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** One version line: `Doctrine: <n>`
- **Durable Summary:** Replaces both proposals ("Spine format: n" and "Doctrine: <skill release>"). An integer: absent = 1. spine-model.md maps each number to its sections and to the skill release that introduced it.
- **Evidence:** Jordi asked for a recorded doctrine version; one line is enough
- **Revisit When:** a third doctrine

## D3

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Doctrine 2 extends 1
- **Durable Summary:** Jordi likes Doctrine 1. Doctrine 2 adds Goal (Mission still counts), Serves, a contributes sentence per child, Done means above the tickets, an `EPIC-<n>:` title and one status.
- **Evidence:** Jordi 2026-10-19
- **Revisit When:** never

## D4

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Start order
- **Durable Summary:** Launching a persona on a spine from the console is the start order; the persona carries the goal to completion. Status reads ready before the launch and active after it.
- **Evidence:** Jordi 2026-10-19
- **Revisit When:** never

## D5

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Define, then plan, then build
- **Durable Summary:** Jordi is not yet sure the doctrine is clear. Step 1 defines it in plain language and resolves ambiguities one question at a time; step 2 is an enforcement plan (scaffold, commit check, version visibility, migration) he approves before any tool work. Former steps 2-5 became 3-6.
- **Evidence:** Jordi via orchestrator 2026-10-19
- **Revisit When:** never

## D6

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** A fresh agent must know what to do
- **Durable Summary:** Jordi asked whether a persona launched against a spine knows what is expected and where to look; today only partly (Next action, Approved work). Added E4-5 (cold-start test on EPIC-4 and poly-maker E4); step 1 puts a `## How to work this` section to Jordi as an open question, recommended yes; the doctrine says an unwritten why is asked of the owner, never invented; step 4 verifies console personas get the always-on block and bind. poly-maker's ad hoc "How to work this epic" note is the precedent.
- **Evidence:** Jordi via orchestrator 2026-10-19
- **Revisit When:** after Jordi answers the How to work this question

## D7

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Step 1 is a coherence pass
- **Durable Summary:** Jordi asked whether EpicSpine is self-consistent and clear; orchestrator says not yet. vps1 scan 2026-10-19: five version-like switches (profile compact 19/full 1, dialect v1 20/v2 4, backend github 11/local 5, Spine Type with 5 `leaf` the validator rejects, Doctrine); this repo declares github tickets but all 31 ledger rows are Issue `draft`, so `--strict` fails here and on 14 of 23 vps1 spines; maintenance duties partial (root Current State was thousands of chars, 15 flat goals); vocabulary drift; ~2,000 lines of skill text against L-1. Doctrine 2 becomes one short page that replaces text; open items (b)-(f) go to Jordi one at a time, each with a recommendation; required = enforced or dropped.
- **Evidence:** orchestrator vps1 scan 2026-10-19
- **Revisit When:** after Jordi answers (b)-(f)

## D8

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** File handoff with EPIC-3
- **Durable Summary:** E3-1 merged; EPIC-3 released spines.py, spine_new.py and pre_commit.py. EPIC-4 cannot touch them before step 2 is approved, so it hands them straight back for E3-2 rather than idling them; step 3 claims them afterwards and builds on E3-2. Step 1 overlaps round 3 (status words, `EPIC-<n>:` rule in spine-model.md), so the doctrine page is drafted only after round 3 merges and takes its wording as given.
- **Evidence:** EPIC-3 manager handoff 2026-10-19
- **Revisit When:** step 2 approved

## D9

- **Date:** 2026-10-20
- **Outcome:** accepted
- **Decision / Attempt:** Outcome contract in snake_case
- **Durable Summary:** The ask proposed camelCase (`doneMeans`, `closedAt`, `closedBy`); the contract uses snake_case (`done_means`, `closed_at`, `closed_by`) like every other `spines.py --json` field. Step 10 runs ahead of steps 1-3: it adds one section and one gate rule, no doctrine rewrite.
- **Evidence:** EPIC-4 manager 2026-10-20
- **Revisit When:** agent_team objects

## D10

- **Date:** 2026-10-20
- **Outcome:** accepted
- **Decision / Attempt:** `current_state` keys follow the field labels
- **Durable Summary:** Each key is the snake_case form of its Current State label, so the ask's `last` becomes `last_attempted`; `evidence` is added because every spine has the line and the console card needs it.
- **Evidence:** EPIC-4 manager 2026-10-20
- **Revisit When:** agent_team objects

## D11

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** No "How to work this" section; the spine is the prototype
- **Durable Summary:** Jordi: a spine is "a snapshot of intent and facts and learnings, plus behaviours for maintenance and for dispatching workers". A generic how-to section confused him; defaults belong at repo or machine level and a spine holds only what is specific to it. His objective: a fresh agent reads the spine alone, knows how to keep going, the state and where the issues are, and builds its own context as needed. Written into the Goal; tested by E4-5. Supersedes the (a) recommendation in "A fresh agent must know what to do".
- **Evidence:** Jordi via orchestrator 2026-10-19
- **Revisit When:** never

## D12

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Root is EPIC-0; one migration
- **Durable Summary:** L-15: the root spine is always EPIC-0. This repo swaps EPIC-2 (root) and EPIC-0 (done audit) as one worker job (step 7), run after the vocabulary is settled so files, headers, links, AGENTS.md and thread briefs migrate once.
- **Evidence:** EPIC-0 L-15 (23f9f30)
- **Revisit When:** never

## D13

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Vocabulary and versioning
- **Durable Summary:** EPIC-0 L-16 (5030649): the tree is objectives and facts hanging from EPIC-0; a leaf is anything linked into it, either an epic (stamped EPIC-<n>, a goal, carries the epic sections; spine = milestone = epic) or a page (unstamped facts/notes, no required structure). Guard: anything stating an intent or goal is an epic, never a page (the poly-maker E4 failure). Learnings are L-<n> assets scoped to their epic. A step is an independently testable mid-outcome, closed only with evidence; Latest Evidence is its test. Unlinked = orphan. Dropped: `Spine Type:`, branch, `Doctrine: <n>`. Answers (b), (e), most of (c) and (f); open: optional header details (profile, dialect, ticket backend); (d) waits for E3-2.
- **Evidence:** EPIC-0 L-16 (fe94053, 5030649)
- **Revisit When:** never

## D14

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** L-16 tree shape
- **Durable Summary:** L-16 refined twice more (30d4bf2 and the swap commit): any leaf may have children at any depth; an epic has exactly one parent (rollup, why-chain, ownership single), a page one or more (any inbound tree link places it, nothing rolls up from a page); any leaf may be referenced from anywhere; status rolls up to the nearest epic ancestor; a closing epic promotes or retires each learning. The doctrine page states these as nouns and boundaries; discovery and orphan rules go in the step 2 plan.
- **Evidence:** Jordi via orchestrator 2026-10-19
- **Revisit When:** never

## D15

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** L-17 tidy, minimal epics
- **Durable Summary:** Answers (d): keep the epic informed after each step, propagate major findings upward, one-line Decisions linking to pages, advisory size budget; EPIC-4 is slimmed first (step 6).
- **Evidence:** EPIC-0 L-17 (root swap commit)
- **Revisit When:** never

## D16

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Compress to the console
- **Durable Summary:** Doctrine page and enforcement plan go to Jordi as one approval (HTML URL); the console contract ([console-contract.md](console-contract.md)) goes to agent_team now, in parallel with step 3; L-15..L-17 become skill doctrine (page + global-block/SKILL.md). Plan: [enforcement.md](enforcement.md).
- **Evidence:** Jordi via orchestrator 2026-10-19
- **Revisit When:** never

## D17

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Personas lost the doctrine
- **Durable Summary:** Tests leaking CLAUDE_CONFIG_DIR and `__file__`-based installer paths broke seat1 hooks and pinned the global pointer to a worktree; fixed as step 9, blocks the E4-3 pipeline check. Console home threads get SessionStart only on first wake (known limit).
- **Evidence:** agent_team pipeline check 2026-10-19
- **Revisit When:** step 9 merged

## D18

- **Date:** 2026-10-21
- **Outcome:** accepted
- **Decision / Attempt:** EPIC-4-A1: doctrine page and enforcement plan
- **Durable Summary:** APPROVED as one, with both small answers yes: advisory size budget 150 lines / 200-char cells; profile, dialect and ticket-backend headers optional. Unblocks step 3 (tools), then 5 and 6.
- **Evidence:** Jordi via agent_team console (item wj_7f4157f90d7b8a48), EPIC-4-A1
- **Revisit When:** never

## D19

- **Date:** 2026-10-22
- **Outcome:** accepted (adopt with changes)
- **Decision / Attempt:** agent_team M2-35 proposal: cross-epic ask references, search before asking, consumed answers
- **Durable Summary:** Problem: Jordi was asked one question several times (EPIC-10-A6 as both a console Needs Jordi item and a coded ask; poly-maker E4-A2/A3 and EPIC-4-A2 the same), and `[answered]` lines stayed in spines and were re-listed every wake. Adopted with these changes:
  1. **Reference, not ask.** A spine blocked by an ask that already exists anywhere writes one Waiting on line `- [waits on <code> row <id>] <one-line gloss>`; across repos the code is qualified `<repo>/<code>` (GitHub repo name, as human-asks.md already does), e.g. `[waits on infra-vps/EPIC-10-A7 row 3]`. It needs no fields, does not count toward the 3-ask limit, and satisfies the "blocked row with no open ask" check. The canonical ask's `unblocks:` may name rows in other epics as `<repo>/<epic code> row <id>`. `spines.py --json` carries a separate per-node `waits_on: [{ref, repo, code, row, state}]`, where `state` is the target ask's state (`open`, `answered`, `done`) when it resolves, else `unresolved`. Checks (advisory): a same-repo code that does not exist warns; a cross-repo code resolves through a sibling checkout (`../<repo>`) and otherwise reports `unresolved` without warning.
  2. **Search before asking.** Before raising an ask, an agent checks the open asks in its repo's tree (`spines.py --json`), in the repos the epic touches, and the console's open Needs Jordi items; if one matches, it references it (rule 1). A console Needs Jordi item and a spine ask for the same question are one ask: the item's question starts with the spine code, never a second code.
  3. **Consumed answers.** After acting on an `[answered …]` line, the owner appends ` · done <YYYY-MM-DD> <sha>` to that line. Tools treat it as closed (`state: "done"`, not listed as work); an `answered` line without `done` is the owner's action item. Deleting the line after its Decisions row exists stays valid.
- **Evidence:** Jordi via agent_team console (M2-35, agent_team docs/spines/m2-team-console.md, docs/handoffs/M2-35-M2-36.md), 2026-10-22
- **Revisit When:** a second cross-repo reference format appears
