# EPIC: Local CLI validation example

This is an illustrative, fully populated v2 spine for learning the workflow. Its roles and draft ticket are examples, not actual assignments. Unchecked SHIP steps deliberately make no delivery-completion claim. For live project execution, use [the audit delivery spine](../docs/EPIC-0-AUDIT-REMEDIATION.md).

Status: ready
Created: 2026-09-06
Updated: 2026-09-06
Repository: AlfaBlok/epicspine-skill
Primary document: EPIC-0-CLI-EXAMPLE.md
Spine ID: cli-onboarding-example
Spine Type: root
Spine dialect: v2
Acceptance surface: cli
Root spine: self
Parent spine: none
Additional root rationale: n/a
GitHub issues: same repository; this illustration has no actual issue
Integration branch: main
Active spine steward: example-manager
Steward since: 2026-09-06 12:00 UTC
Last reconciled commit: d6a6d026430bab11430986a9258f85844564f8b4
Planner: example-manager
Worker: example-manager
Tester: example-tester

## Role Bindings

Epic worker: example-manager is the MANAGER; dispatch workers, integrate results, and walk the SHIP journey personally.
Ticket worker: example-worker. FIRST ACTION: `git worktree add /tmp/wt-cli-example -b codex/cli-example d6a6d026430bab11430986a9258f85844564f8b4`; never checkout/switch in the shared clone. Inspect PORT/DUPLICATE sources; record adaptations and validation.
Tester: example-tester validates the exact commit against the assigned acceptance.

## Write Scope

Bound spine: this document. Only example-manager would steward this spine; sample workers and testers would report to their assigned issue. No role is actually dispatched by this illustration.

## Authority By Artifact

This spine owns illustrative intent and rollup state. Issues own execution detail; code owns implementation; command evidence owns what was proved. The one steward reconciles contradictions.

## Spine Map

No child spines.

## Mission

Give a new contributor one local, reproducible CLI journey for reading a populated spine, validating it, and running the package regression suite. All commands below run from the repository root with Python 3.10+ and no additional dependencies.

## Definition Of Done

SHIP — the manager personally executes this CLI journey: run → first failure → dispatch a scoped fix → prepare the updated surface → restart from step 1 until one uninterrupted clean pass.
Acceptance outcome: The documented validator commands return their expected results.
Evidence method: cli: Save the invocation, supplied fixture, return status and terminal transcript.

- [ ] 1. Run `python3 skill/epic-spine/scripts/validate_spine.py --help`; expect usage text and exit code 0 — PORT from the existing validator.
- [ ] 2. Run `python3 skill/epic-spine/scripts/validate_spine.py --strict examples/EPIC-0-CLI-EXAMPLE.md`; expect `OK` and exit code 0 — PORT from the existing local validation command.
- [ ] 3. Run `python3 skill/epic-spine/scripts/validate_spine.py --strict --graph examples/EPIC-0-CLI-EXAMPLE.md`; expect `OK` and exit code 0 for this standalone root — PORT from the existing graph validator.
- [ ] 4. Run `python3 -B -m unittest discover -s tests -v`; expect all tests passing and exit code 0 — PORT from the existing regression suite.
- [ ] 5. Test package: record personally verified steps, exact commit from `git rev-parse HEAD`, named environment from `python3 --version`, command results and remaining limits. Inputs are the tracked example and tests. The local commands do not verify GitHub state or launch a product. These unchecked steps do not claim completion.

HARDEN — deferred until the human approves SHIP:

- [ ] Add performance benchmarks for large spine graphs.

## Current State

Phase: planning
Fresh base commit: d6a6d026430bab11430986a9258f85844564f8b4
Pinned-base rule: pinned; no rebases until the journey passes.
Dispatch condition: none
Next action: Run the first documented CLI command.
Blockers: none

## Execution Cursor

Last attempted: Populated this illustrative spine.
Result: The example describes a reproducible local journey; no real assignment or accepted delivery is recorded.
Execution status: ready
Waiting on: nothing
Approved work: Read the example and run local validation commands; no dispatch or external mutation.
Next action: Run the first documented CLI command.

## Bootstrap Map

1. Read this document for the sample acceptance and ownership.
2. Read [the README](../README.md) for installation and validation options.
3. Read [the skill](../skill/epic-spine/SKILL.md) for the full operating rules.

## Architecture And Context

Search scope: current epicspine-skill repository only
Search budget: 15 minutes
Search evidence: inspected skill/epic-spine/scripts/validate_spine.py and tests/test_validate_spine.py; under the 15-minute budget; inspected the populated v2 fixture and CLI help as well. No external implementation repositories/services required or searched; no absence claim about them.
Method rationale: PORT the existing validator and regression workflow; DUPLICATE the populated v2 fixture structure with example-specific roles and commands. No runtime dependency or invented issue is needed.

Waves: Wave 1: validator exercise. Wave 2: regression exercise. Then the manager executes the journey loop; file ownership is disjoint.
Heartbeat every 30 minutes: `lap/state | blocker | ETA`; two consecutive ETA slips stop the thread and report options.
Proportional ceremony: live customer data requires snapshot + checksum + restore drill; reversible test assets use snapshot-and-go; documentation requires none.

## Decisions

| ID | Date | Outcome | Decision / Attempt | Durable Summary | Rule / Absence Rule | Evidence | Revisit When |
|---|---|---|---|---|---|---|---|
| D1 | 2026-09-06 | accepted | Use existing validator | Keep the example executable with Python only. | PORT existing validation. | skill/epic-spine/scripts/validate_spine.py | Validator contract changes |
| D2 | 2026-09-06 | accepted | Routine defaults | Preserve bounded autonomy. | Choose safe reversible options within approved scope and journal uncertainty; required approvals remain gates. | This example specification | Scope changes |

## Issue Ledger

| Issue | Wave | Method | Budget | Role | Owner / Assignment | Title | Status | Depends On | Worktree | PR/Branch | Base | Acceptance | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| draft | 1 | PORT from skill/epic-spine/scripts/validate_spine.py | 90 min | Ticket worker | example-worker | Run CLI command journey | draft | none | /tmp/wt-cli-example | codex/cli-example | d6a6d026430bab11430986a9258f85844564f8b4 | Journey steps 1–4 pass | Illustrative plan only | 2026-09-06 12:00 UTC | Create an actual issue only after explicit assignment |

## Branch And Integration

Integration target is main for a future real assignment. Create a dedicated worktree from the pinned base before editing, and preserve shared-checkout state. No merge is authorized by this illustrative document.

## Human Gates

| Gate | Human Owner | Trigger | Exact Approval / Input Required | What May Continue |
|---|---|---|---|---|
| Expand scope | Example owner | Work exceeds this CLI example | Approval of the concrete new scope | Existing example validation |

Report BLOCKED ON the owner with exact input and evidence; stop dependent work and continue only independent authorized work. Silence never supplies required approval. No gate currently blocks the planned example acceptance.

## Recovery And Takeover

The manager reassigns tickets silent past budget after preserving issue evidence and commits.

## Validation Evidence

Illustrative planning state only. Run the SHIP commands against the current checkout and record fresh commit/environment evidence before marking any delivery accepted.

## Handoff Journal

Illustrative planning state only. Run the SHIP commands against the current checkout and record fresh commit/environment evidence before marking any delivery accepted.

## Open Questions

None.

## Appendix

Inputs from human: no input is currently needed. Absence rule: run authorized local example validation; new scope remains a gate.

### Worker Dispatch Prompts v1

Illustrative prompt only; do not dispatch the draft ticket. Ticket worker example-worker: bound spine examples/EPIC-0-CLI-EXAMPLE.md, draft ledger row, steward example-manager. Inherit dialect v2 and acceptance surface cli. After an actual issue and assignment exist, use dedicated worktree /tmp/wt-cli-example from d6a6d026430bab11430986a9258f85844564f8b4; run the assigned CLI journey, record commands, results, commit and limits. Human Gates apply to any expanded scope. Terminal state is tested handoff. Go.
