# EPIC-6: Status-true spines: the checker catches what makes the console status lie

Spine profile: compact
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-6-STATUS-TRUE-SPINES.md
Spine ID: status-true-spines-the-checker-catches-what-makes-the-console-status-lie
Root spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Parent spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main
Integration policy: main-direct

## Goal

`validate_spine.py` flags the three spine shapes that make the agent_team console status lie (free-text asks naming Jordi, `done` with unticked Done means, 'nothing open for Jordi' beside an open coded ask), and the references and prompt snippets show the coded-ask format once. Origin: agent_team docs/spines/epic-13-one-status-model.md (step E13-S5), design http://100.86.141.63:58213/index.html slide 9.

## Serves

[EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md): keeps the repo's validator honest about what the console reads; serves agent_team EPIC-13 (E13-2, E13-5).

## Done means

- [x] E6-1 `validate_spine.py` raises an advisory (promoted by `--strict`) for each of the three shapes, one positive and one negative fixture each; the existing suite stays green; verified by running it over agent_team's `docs/spines/*.md` and reporting the counts (2026-10-24: 1174c69, merge 44ab11e; tests/test_status_true.py 7 tests; 682 OK; agent_team 4 advisories, this repo 0)
- [x] E6-2 `references/` and the prompt snippets show the coded-ask format and the three rules once, briefly; `assets/global-block.md` size unchanged (2026-10-24: 1174c69: one line in spine-model.md, one in dispatch-prompt-preamble.md; global-block.md untouched)

## Current State

Owner: Delivery Manager (agent-team console)
Status: active
Last attempted: 2026-10-24 DM wake run_aa2dd0a3: E6-S1 (run_98fc838e) verified and merged (44ab11e)
Result: both Done means met; Outcome written; awaiting verification
Evidence: 1174c69, c804f48, merge 44ab11e; 682 tests OK; graph --strict 0 errors
Waiting on: nobody
Approved work: none
Next action: Jordi verifies the Outcome and sets done; agent_team fixes its 4 advisories and records E13-S5 evidence in its own thread (L-14)
Source revision: main
Verified at: 2026-10-24

## Outcome

Verdict: accomplished
Outcome: `validate_spine.py` now flags the three spine shapes that made the console status lie (free-text asks naming Jordi, done with unticked Done means, "nothing open" beside an open ask), as advisories `--strict` promotes, and spine-model.md plus the dispatch preamble state the rules once.
Closed: 2026-10-24 by run_aa2dd0a3-0bdd-4c5c-bc6c-79b32cba5e50
Risk: agent_team has 4 advisories to fix (epic-7-team-url, m5-unblocked-web, root, epic-12 row 3); the human name `Jordi` is fixed in personas.py; done-row check fires only when a row cites an unticked criterion ID.

| Done means | Evidence |
|---|---|
| E6-1 | 1174c69 (status_true.py, 7 fixture tests), merge 44ab11e: 682 tests OK; agent_team 4 advisories, this repo 0 |
| E6-2 | 1174c69: spine-model.md + dispatch-prompt-preamble.md one line each; global-block.md unchanged |

## Non-Goals

Not changing the console, and not rewriting other repos' spines (the worker only reports the advisory counts).

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker run_98fc838e (Sonnet 5.5, seat1) | E6-S1 (= agent_team E13-S5b) spine checker advisories + references; brief docs/handoffs/2026-10-24-e13-s5b-spine-checker.md | done | none | merged (branch deleted) | main | 1174c69, merge 44ab11e; DM verified 682 OK, graph --strict 0 | 2026-10-24 | none |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |
| 2026-10-24 | accepted | decided by Delivery Manager: done-row check fires only when the row cites an unticked criterion ID; `Waiting on:` free text counts as an ask line; a Jordi-owned row is covered by an open ask naming it or with no row — why: flagging every done row in an open epic is noise — rollback: widen the check in status_true.py | worker interpretations accepted on review | 1174c69 | console shows a false status anyway |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
