# EPIC: Test

Status: ready
Created: 2026-08-16
Updated: 2026-08-16
Repository: example/repo
Primary document: EPIC-GITHUB-TICKETS.md
Spine ID: synthetic-github-tickets
Spine Type: root
Spine dialect: v1
Ticket backend: github
Root spine: self
Parent spine: none
Additional root rationale: n/a
GitHub issues: example/repo/issues
Integration branch: main
Active spine steward: codex-test
Steward since: 2026-08-16 12:00 UTC
Last reconciled commit: abc1234
Planner: codex-test
Worker: codex-test
Tester: codex-test

## Role Bindings

Planner: fixture-planner. Ticket worker: fixture-worker. Tester: fixture-tester. The planner is the only spine steward.

## Write Scope

Bound spine: this document

## Authority By Artifact

This spine owns intent and rollup state.

## Spine Map

No child spines.

## Mission

Demonstrate the existing GitHub ticket backend using a synthetic offline issue snapshot. URL structure is checked; no issue existence or remote status is verified.

## Definition Of Done

- [ ] Graph validation passes.

## Current State

Phase: implementation
Next action: Run validation.

## Execution Cursor

Last attempted: Created the fixture.
Result: Fixture is ready.
Execution status: ready
Waiting on: nothing
Approved work: Run all validation tests.
Next action: Run validation.

## Bootstrap Map

Read this document.

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-08-16 | accepted | Use the connected hierarchy | It gives every branch one owner. | issue-1 | n/a |

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Acceptance | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [#1](https://github.com/example/repo/issues/1) | Ticket worker | fixture-worker | Validate graph | ready | none | codex/fixture | abc1234 | Graph checks pass | Fixture specification | 2026-08-16 12:00 UTC | Run tests |

## Branch And Integration

Integration target is main.

## Human Gates

None.

## Recovery And Takeover

Resume from the cursor.

## Validation Evidence

Fixture assembled for automated validator acceptance; no product execution is claimed.

## Handoff Journal

Fixture assembled for automated validator acceptance; no product execution is claimed.

## Open Questions

None.
