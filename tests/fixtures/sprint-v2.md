# EPIC: Test

Status: ready
Created: 2026-08-16
Updated: 2026-08-16
Repository: example/repo
Primary document: sprint-v2.md
Spine ID: sprint-v2
Spine Type: root
Spine dialect: v2
Acceptance surface: cli
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

Epic worker: fixture-manager is the MANAGER; dispatch workers, integrate results, and walk the SHIP journey personally.
Ticket worker: fixture-worker. FIRST ACTION: `git worktree add ../wt-fixture -b codex/fixture abc1234`; never checkout/switch in the shared clone. Inspect PORT/DUPLICATE sources; record adaptations and validation.
Tester: fixture-tester validates the exact commit against the assigned acceptance.

## Write Scope

Bound spine: this document

## Authority By Artifact

This spine owns intent and rollup state.

## Spine Map

No child spines.

## Mission

Prove the connected-spine contract.

## Definition Of Done

SHIP — the manager personally executes this CLI journey: run → first failure → dispatch a scoped fix → prepare the updated surface → restart from step 1 until one uninterrupted clean pass.
Evidence: exact commands, inputs, exit codes and outputs.

- [ ] 1. Run the validator help command — PORT from skill/epic-spine/scripts/validate_spine.py.
- [ ] 2. Validate this fixture locally — PORT from tests/fixtures/sprint-v2.md.
- [ ] 3. Run graph validation on the legacy fixture — PORT from tests/fixtures/legacy-v1.md.
- [ ] 4. Run the regression suite — PORT from tests/test_validate_spine.py.
- [ ] 5. Test package: personally verified steps, exact commit, named environment, command results, remaining limits and reproducible instructions. Execution evidence is required before acceptance; these unchecked steps do not claim completion.

HARDEN — deferred until the human approves SHIP:

- [ ] Add performance benchmarks for large spine graphs.

## Current State

Phase: planning
Fresh base commit: abc1234
Pinned-base rule: pinned; no rebases until the journey passes.
Dispatch condition: none
Next action: Run validation.
Blockers: none

## Execution Cursor

Last attempted: Created the fixture.
Result: Fixture is ready.
Execution status: ready
Waiting on: nothing
Approved work: Run all validation tests.
Next action: Run validation.

## Bootstrap Map

Read this document.

## Architecture And Context

Search scope: current epicspine-skill repository only
Search budget: 15 minutes
Search evidence: inspected skill/epic-spine/scripts/validate_spine.py and tests/test_validate_spine.py; 5 minutes; no external services required or searched.
Method rationale: PORT existing validator and fixture tests; no new runtime dependency.

Waves: Wave 1: validator exercise. Wave 2: regression exercise. Then the manager executes the journey loop; file ownership is disjoint.
Heartbeat every 30 minutes: `lap/state | blocker | ETA`; two consecutive ETA slips stop the thread and report options.
Proportional ceremony: live customer data requires snapshot + checksum + restore drill; reversible test assets use snapshot-and-go; documentation requires none.

## Decisions

| ID | Date | Outcome | Decision / Attempt | Durable Summary | Rule / Absence Rule | Evidence | Revisit When |
|---|---|---|---|---|---|---|---|
| D1 | 2026-08-16 | accepted | Use existing validator | Keep the fixture executable with Python only. | PORT existing validation. | skill/epic-spine/scripts/validate_spine.py | Validator contract changes |
| D2 | 2026-08-16 | accepted | Routine defaults | Preserve bounded autonomy. | Choose safe reversible options within approved scope and journal uncertainty; required approvals remain gates. | This fixture specification | Scope changes |

## Issue Ledger

| Issue | Wave | Method | Budget | Role | Owner / Assignment | Title | Status | Depends On | Worktree | PR/Branch | Base | Acceptance | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [#1](https://github.com/example/repo/issues/1) | 1 | PORT from skill/epic-spine/scripts/validate_spine.py | 90 min | Ticket worker | fixture-worker | Run CLI command journey | ready | none | /tmp/wt-fixture | codex/fixture | abc1234 | Journey steps 1–4 pass | Fixture specification | 2026-08-16 12:00 UTC | Run the acceptance commands |

## Branch And Integration

Integration target is main.

## Human Gates

| Gate | Human Owner | Trigger | Exact Approval / Input Required | What May Continue |
|---|---|---|---|---|
| Expand scope | Fixture owner | Work exceeds this CLI fixture | Approval of the concrete new scope | Existing fixture validation |

Report BLOCKED ON the owner with exact input and evidence; stop dependent work and continue only independent authorized work. Silence never supplies required approval. No gate currently blocks the planned fixture acceptance.

## Recovery And Takeover

The manager reassigns tickets silent past budget after preserving issue evidence and commits.

## Validation Evidence

Fixture assembled for automated validator acceptance; no product execution is claimed.

## Handoff Journal

Fixture assembled for automated validator acceptance; no product execution is claimed.

## Open Questions

None.

## Appendix

Inputs from human: no input is currently needed. Absence rule: run authorized fixture validation; new scope remains a gate.

### Worker Dispatch Prompts v1

Ticket worker fixture-worker: bound spine sprint-v2.md, issue example/repo#1, steward fixture-manager. Use dedicated worktree /tmp/wt-fixture from abc1234; run the assigned CLI journey, record commands, results, commit and limits. Human Gates apply to any expanded scope. Terminal state is tested handoff. Go.
