# EPIC: Explain the local validator

Spine profile: compact
Spine dialect: v1
Repository: example/validator
Primary document: EPIC-COMPACT-EXAMPLE.md
Spine ID: synthetic-compact-example
Integration branch: codex/example

## Current State

Owner: example-steward
Status: ready
Last attempted: Drafted the synthetic CLI explanation.
Result: The acceptance command and one work item are ready for review.
Evidence: [Synthetic history](EPIC-COMPACT-HISTORY.md#draft-review)
Waiting on: none
Approved work: Read and validate this synthetic example locally.
Next action: Run the validator against this file.
Source revision: 6f63d378e0ed8e8adffdda89039f8a0c16069909
Verified at: 2026-09-06T14:00:00Z

## Mission

Let a cold reader locate the owner, waiting condition and next action without reading a handoff journal. This example is synthetic, not a real assignment or completion claim.

## Non-Goals

No deployment, remote ticket mutation, hierarchy claim or installed-skill change.

## Definition Of Done

- [ ] Run `python3 skill/epic-spine/scripts/validate_spine.py --strict examples/EPIC-COMPACT-EXAMPLE.md` from the package root and record the exit code against the tested revision.

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | example-worker | Review CLI explanation | draft | none | codex/example | 6f63d378 | Synthetic draft only | 2026-09-06 | Read acceptance command |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-09-06 | rejected | Duplicate current state in a handoff | One state block avoids drift. | [Draft review](EPIC-COMPACT-HISTORY.md#draft-review) | Never for manually maintained copies |

## Handoff Journal

[Completed synthetic handoff](EPIC-COMPACT-HISTORY.md#draft-review). Current facts remain in [Current State](#current-state).
