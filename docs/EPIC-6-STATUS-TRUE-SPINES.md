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

- [ ] E6-1 `validate_spine.py` raises an advisory (promoted by `--strict`) for each of the three shapes, one positive and one negative fixture each; the existing suite stays green; verified by running it over agent_team's `docs/spines/*.md` and reporting the counts
- [ ] E6-2 `references/` and the prompt snippets show the coded-ask format and the three rules once, briefly; `assets/global-block.md` size unchanged

## Current State

Owner: unassigned
Status: ready
Last attempted: scaffolded with spine_new.py on 2026-10-24
Result: created, not started
Evidence: EPIC-0-OPERATING-SYSTEM.md
Waiting on: none
Approved work: none
Next action: Delivery Manager dispatches a worker on E6-S1 (brief docs/handoffs/2026-10-24-e13-s5b-spine-checker.md)
Source revision: see git log
Verified at: 2026-10-24

## Non-Goals

Not changing the console, and not rewriting other repos' spines (the worker only reports the advisory counts).

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | seat pool | E6-S1 (= agent_team E13-S5b) spine checker advisories + references; brief docs/handoffs/2026-10-24-e13-s5b-spine-checker.md | ready | none | none | main | brief written 2026-10-24 | 2026-10-24 | Delivery Manager dispatches a worker |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
