# <ticket title>

EpicSpine: <link or path>
Role: Epic 0 worker | planner | epic worker | ticket worker | tester
Assigned identity: <agent/thread/name>
Status: ready
Depends on: <issue links or none>
Bound spine: <same as EpicSpine unless explicitly different>
Branch / worktree: <branch name, worktree path, or TBD>
Integration target: main

## Goal

Describe the ticket outcome in one short paragraph.

Terminal state: ready for testing | accepted | blocked with required input | planner decision required

## Context

- Spine section: <heading or anchor>
- Required reads: <links copied from the Bootstrap Map>
- Prior decision: <decision link or none>

Use this issue for detailed ticket work: code paths, blockers, logs, review discussion, and implementation notes. Write back to the EpicSpine only when this work changes durable intent, scope, state, dependency, risk, evidence, or next action.

## Acceptance Criteria

- [ ] <observable ticket-level criterion>
- [ ] <observable ticket-level criterion>

## Validation

Required evidence:

- [ ] <test command, review method, screenshot, or deployment check>

## Handoff Contract

When done, update the EpicSpine:

- [ ] Issue Ledger status, PR/branch, evidence, and next action
- [ ] Handoff Journal entry
- [ ] Validation Evidence if testing was performed
- [ ] Proposed Cross-Spine Updates if this work reveals changes needed in read-only spines
- [ ] Merge or PR status against the integration branch

## Notes

<optional constraints, risks, or implementation notes>
