# EPIC: Compare two synthetic research protocols

Spine profile: compact
Spine dialect: v1
Ticket backend: local
Ticket root: tickets
Repository: example/research
Primary document: EPIC-LOCAL-RESEARCH.md
Spine ID: synthetic-local-research
Integration branch: codex/research-example

## Current State

Owner: example-research-steward
Status: ready
Last attempted: Wrote two synthetic protocol tickets.
Result: Each ticket file owns its own status, owner and evidence.
Evidence: [Protocol record](protocol.md)
Waiting on: none
Approved work: Read these synthetic files and validate local references.
Next action: Read the R-001 ticket acceptance.
Source revision: 6512dce8c202ff9bc79730adc2f83ec8e5835ddd
Verified at: 2026-09-06T15:00:00Z

## Mission

Demonstrate a local research board with concrete ticket identities and one authoritative file per ticket. No real research result or execution assignment is claimed.

## Non-Goals

No real dataset, private repository import, remote issue update or profitability claim.

## Definition Of Done

- [ ] Run `python3 skill/epic-spine/scripts/validate_spine.py --strict examples/local-research/EPIC-LOCAL-RESEARCH.md`; expect local ticket references to resolve with exit code 0.

## Issue Ledger

| Ticket | Depends On |
|---|---|
| [R-001](tickets/R-001.md) | none |
| [R-002](tickets/R-002.md) | R-001 |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-09-06 | accepted | Local ticket authority | The ledger stores links/dependencies; files own mutable ticket facts. | [Protocol record](protocol.md) | Backend changes explicitly |
