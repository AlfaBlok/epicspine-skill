# EPIC-8: Closed epics close their rows; tree audit

Spine profile: compact
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-8-CLOSED-EPICS-CLOSE-ROWS.md
Spine ID: closed-epics-close-their-rows-tree-audit
Root spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Parent spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main
Integration policy: main-direct

## Goal

A finished epic shows no open work: ledger rows get a closed-not-done status `superseded`, closing an epic sweeps its open rows to it, the validator advises on a finished epic with open rows, and `tree_audit.py` reports any repo's stale tree with the exact sweep command. Origin: agent_team docs/spines/epic-16-clean-spine-trees.md (E16-S1; Jordi 2026-10-24: zenod closed 22 of 30 epics yet ~95 rows inside them still read as live work).

## Serves

[EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md): the skill owns the row vocabulary and the cleanse mechanism, so every repo with stale spines fixes them at the source; Serves: agent_team EPIC-16 https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-16-clean-spine-trees.md (E16-1, step E16-S1).

## Done means

- [x] E8-1 Row status `superseded` (closed, not done) in the vocabulary (spine-model, persona-tasks, `spine_fix` synonyms, trackable, rollup) and `spine_fix.py --close [--write]` sweeps a finished epic's open rows to it with a Next Action note, dry run by default, idempotent; tests in tests/test_close_rows.py
- [x] E8-2 `validate_spine.py` advises `closed-rows:` (never a block) and `tree_audit.py --repo DIR [--json]` reports the seven groups plus the sweep command; proof run on a zenod copy reported
- [x] E8-3 Playbook references/tree-cleanse.md linked from SKILL.md; release rolled out per SYNC.md with the host list reported

## Current State

Owner: Delivery Manager (agent_team brief docs/handoffs/E16-S1.md)
Status: done
Last attempted: 2026-10-24 Delivery Manager merged wt/e16-s1-close-rows (6e1abf7), re-ran tests, checked rollout
Result: E8-1, E8-2 met on branch wt/e16-s1-close-rows (skill 2026.10.24.10, 715 tests OK, graph --strict 0 errors); proof on a zenod copy: 18 finished epics, 80 open rows swept, re-run 0; E8-3 met: merged 6e1abf7, 715 tests OK on the merge; VERSION 2026.10.24.10 in vps3 and vps1 ~/.claude, ~/.claude_seat1, ~/.claude_seat2 (6/6); tree_audit on real zenod: 22 finished epics, 107 open rows
Evidence: 3ba2722 vocabulary, 78f6201 sweep + advisory, 72320d0 tree_audit + playbook + tests, 18b2d9d release .10
Waiting on: none
Approved work: E8-S1 (brief docs/handoffs/E16-S1.md in agent_team)
Next action: none (closed). zenod's vendored copy re-sync and its sweep are agent_team E16-S3.
Source revision: main 6e1abf7
Verified at: 2026-10-24

## Outcome

Verdict: accomplished
Outcome: A finished epic can no longer show open work: rows have a `superseded` status, `spine_fix.py --close` sweeps a closed epic's open rows, `validate_spine.py` advises `closed-rows:`, and `tree_audit.py` + references/tree-cleanse.md let any repo audit and cleanse its tree.
- E8-1: 3ba2722, 78f6201; tests/test_close_rows.py (715 tests OK on merge 6e1abf7)
- E8-2: 72320d0; zenod copy proof (80 rows / 18 epics, re-run 0) and real zenod audit (107 rows / 22 epics) 2026-10-24
- E8-3: references/tree-cleanse.md linked from SKILL.md; release 2026.10.24.10 on vps3 + vps1, 3 config dirs each
Risk: vendored copies (zenod/skills/epic-spine) re-sync per SYNC.md in each repo's own thread (zenod: agent_team E16-S3); `integrated`/`resolved` now autofix to `done` in every repo's pre-commit.
Closed: 2026-10-24, Delivery Manager (agent_team EPIC-16)

## Non-Goals

Not writing any repo's spines (each repo sweeps its own, e.g. zenod in agent_team E16-S2); not changing the agent_team console.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker (Opus 5.5) | E8-S1 superseded row status, sweep on close, advisory, tree_audit, playbook, release; brief docs/handoffs/E16-S1.md (agent_team) | done | none | merged 6e1abf7 | main | 3ba2722, 78f6201, 72320d0, 18b2d9d; 715 tests OK, graph --strict 0 errors; zenod copy 80 rows / 18 epics | 2026-10-24 | none |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |
| 2026-10-24 | accepted | Status active on DM dispatch (as EPIC-7), not a self-ready | the brief is the start order | agent_team docs/handoffs/E16-S1.md | never |
| 2026-10-24 | accepted | Sweep is `spine_fix.py --close` (body close_rows.py), not rollup_spine.py; `closed-rows:` advisory not strict-promoted; `superseded` also a trackable epic Status | spine_fix owns row words; brief says never a block; run_state/outcome already treat it as closed | 78f6201, 3ba2722 | never |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
