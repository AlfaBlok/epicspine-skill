# EPIC: Synthetic root rollup source

Spine profile: compact
Spine dialect: v1
Repository: example/validator
Primary document: root.md
Spine ID: root
Integration branch: codex/example
Spine Type: root
Root spine: self
Parent spine: none
Additional root rationale: n/a

## Current State

Owner: steward-root
Status: ready
Last attempted: Drafted the synthetic CLI explanation.
Result: The acceptance command and one work item are ready for review.
Evidence: [Acceptance](#definition-of-done)
Waiting on: none
Approved work: Read and validate this synthetic example locally.
Next action: Run the validator against this file.
Source revision: 6f63d378e0ed8e8adffdda89039f8a0c16069909
Verified at: 2026-09-06T14:00:00Z

## Mission

Demonstrate one-level execution projections and descendant freshness. This graph is synthetic, not a real assignment or completion claim.

## Non-Goals

No deployment, remote ticket mutation, semantic parent decision or installed-skill change.

## Definition Of Done

- [ ] Run `python3 skill/epic-spine/scripts/validate_spine.py --strict examples/EPIC-COMPACT-EXAMPLE.md` from the package root and record the exit code against the tested revision.

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | example-worker | Review CLI explanation | draft | none | codex/example | 6f63d378 | Synthetic draft only | 2026-09-06 | Read acceptance command |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-09-06 | rejected | Duplicate current state in a handoff | One state block avoids drift. | [Draft review](../EPIC-COMPACT-HISTORY.md#draft-review) | Never for manually maintained copies |

## Handoff Journal

[Completed synthetic handoff](../EPIC-COMPACT-HISTORY.md#draft-review). Current facts remain in [Current State](#current-state).

## Spine Map

| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |
|---|---|---|---|---|---|---|---|---|
| child | child | [child](child.md) | Preserve `purpose-child` | ready | healthy | pending | 2026-09-06 | Previous projection |
