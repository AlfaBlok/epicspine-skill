# EPIC 0: Audit remediation

Status: review
Created: 2026-09-06
Updated: 2026-09-06
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-0-AUDIT-REMEDIATION.md
Spine ID: epicspine-audit-remediation
Spine Type: root
Root spine: self
Parent spine: none
Additional root rationale: n/a
Spine dialect: v1
Acceptance surface: cli
Integration branch: codex/audit-remediation
Active spine steward: /root delivery manager
Last reconciled commit: df3908e568b12f10abb3182027f9c6f1a35d4699

## Role Bindings

The user bound /root as delivery manager on 2026-09-06 and explicitly authorized issue creation and subagent delivery. /root creates backlog, dispatches, reviews evidence and integrates; it does not implement fixes. Ticket workers own remediation in separate worktrees. A tester independently validates the integrated result.

## Write Scope

Only /root edits this spine. Workers edit only their issue's assigned files and write detailed progress to GitHub issues. The primary checkout and installed skills remain untouched. Book binding: inactive.

## Authority By Artifact

This spine owns scope, dependencies and rollup state. GitHub issues own ticket detail. Commits own implementation; test evidence owns validation claims.

## Spine Map

No child spines.

## Mission

Remediate the six audit work packages through subagents, preserving artifact authority, one steward, execution cursors and connected-spine navigation. Deliver a tested reviewable branch and report outcomes to the user.

## Definition Of Done

- [x] Malformed Markdown rows cannot disappear from validation; empty values cannot consume following fields.
- [x] Explicit dialect selection preserves strict legacy compatibility and enforces the selected acceptance surface.
- [x] Non-draft issue references and ledger statuses are checked with regressions.
- [x] Workflow rules use bounded relevant discovery and surface-appropriate personal verification.
- [x] A complete example and quickstart validate locally; CI runs the regression suite.
- [x] Independent tester verifies the integrated commit; final PR and residual risks are reported.

Acceptance is the local Python CLI and documentation package. No live product exists to deploy. Browser screenshots are not evidence for this repair. This scope follows the user's authorization to remediate the audited universal-browser requirement.

## Current State

Phase: review
Integration target: codex/audit-remediation
Fresh base commit: df3908e568b12f10abb3182027f9c6f1a35d4699 (frozen implementation acceptance revision)
Dispatch condition: all six tickets delivered; no queued implementation.
Next action: Review PR #16; preserve tested implementation while awaiting merge decision.
Blockers: none

## Execution Cursor

Last attempted: Independent tester exercised all six acceptance packages at the frozen implementation revision.
Result: All six packages pass; 34 tests on Python 3.10 and 3.14, strict CLI checks, sandbox install checks and hosted CI pass.
Execution status: review
Waiting on: PR review and merge decision; no implementation blockers
Approved work: Review followup and coordination within existing remediation scope; manager remains available.
Next action: Review PR #16; preserve tested implementation while awaiting merge decision.

## Bootstrap Map

1. Read this spine and the assigned GitHub issue.
2. Read skill/epic-spine/SKILL.md as the implementation being repaired; issue acceptance resolves audited conflicts.
3. Read the assigned code/templates and tests/test_validate_spine.py.
4. Read references/operating-model.md for shared vocabulary.

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-09-06 | accepted | Manager does not implement | All fixes belong to subagents; manager owns coordination and integration. | User request in current task | User changes role |
| 2026-09-06 | accepted | Bounded discovery | Search this package and relevant local sources; no unrelated account-wide inventory. | Audit and issue #13 | A concrete dependency emerges |
| 2026-09-06 | accepted | CLI acceptance | Personally execute the actual validator and documented commands; no unrelated deployment. | Issue #13 | A browser product is added |
| 2026-09-06 | accepted | Serial code ownership | Parser then dialect then ledger; workflow and CI run independently. | Shared validator and test files | Ownership can be separated |
| 2026-09-06 | accepted | Dialect contract | Spine dialect v1/v2; --dialect auto/v1/v2; undeclared defaults to v1. Acceptance surface browser/cli/library/infrastructure/documentation. | Issue #11 | Regression evidence requires revision |
| 2026-09-06 | accepted | Review boundary | Produce reviewed integration PR; no production deployment or installed-skill update. | Approved remediation scope | User requests rollout |

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Acceptance | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [#10](https://github.com/AlfaBlok/epicspine-skill/issues/10) | Ticket worker | /root/parser | Fix Markdown parsing so malformed rows and empty fields cannot bypass validation | review | none | [PR #16](https://github.com/AlfaBlok/epicspine-skill/pull/16); codex/audit-parser | 88c3c0cf3cff02bc36a8c11234a27f2a7450a0c5 | Issue acceptance | 44140186; independent acceptance PASS at df3908e | 2026-09-06 | Merge review; closes on PR merge |
| [#11](https://github.com/AlfaBlok/epicspine-skill/issues/11) | Ticket worker | /root/parser | Separate dialect selection from strictness and add real v1/v2 compatibility fixtures | review | #10, #13 | [PR #16](https://github.com/AlfaBlok/epicspine-skill/pull/16); codex/audit-dialect | 0381c809ed7a704c04dadb4fb7cd50344e15ac41 | Issue acceptance | 037df981; independent acceptance PASS at df3908e | 2026-09-06 | Merge review; closes on PR merge |
| [#12](https://github.com/AlfaBlok/epicspine-skill/issues/12) | Ticket worker | /root/parser | Validate non-draft issue references and ledger status vocabulary | review | #11 | [PR #16](https://github.com/AlfaBlok/epicspine-skill/pull/16); codex/audit-ledger | 0df5e291a2c069b864f1a91201dfe6ffcb7b3e40 | Issue acceptance | 55642bc0; independent acceptance PASS at df3908e | 2026-09-06 | Merge review; closes on PR merge |
| [#13](https://github.com/AlfaBlok/epicspine-skill/issues/13) | Ticket worker | /root/workflow | Scope acceptance to the delivery surface and bound reuse discovery | review | none | [PR #16](https://github.com/AlfaBlok/epicspine-skill/pull/16); codex/audit-workflow | 88c3c0cf3cff02bc36a8c11234a27f2a7450a0c5 | Issue acceptance | b1ce6d23; independent acceptance PASS at df3908e | 2026-09-06 | Merge review; closes on PR merge |
| [#14](https://github.com/AlfaBlok/epicspine-skill/issues/14) | Ticket worker | /root/workflow | Add a short installation quickstart and a completed runnable example | review | #11, #12, #13 | [PR #16](https://github.com/AlfaBlok/epicspine-skill/pull/16); codex/audit-onboarding | d6a6d026430bab11430986a9258f85844564f8b4 | Issue acceptance | bfbc2617; independent acceptance PASS at df3908e | 2026-09-06 | Merge review; closes on PR merge |
| [#15](https://github.com/AlfaBlok/epicspine-skill/issues/15) | Ticket worker | /root/ci | Run validator regression tests in GitHub Actions | review | none | [PR #16](https://github.com/AlfaBlok/epicspine-skill/pull/16); codex/audit-ci | 88c3c0cf3cff02bc36a8c11234a27f2a7450a0c5 | Issue acceptance | 42e7e143; independent acceptance PASS at df3908e | 2026-09-06 | Merge review; closes on PR merge |

## Branch And Integration

Manager worktree: /Users/jordi/Documents/GitHub/epicspine-audit-manager. Worker branches are codex/audit-{ticket}; separate worktrees are required. Integration target is codex/audit-remediation, with final PR targeting main. Manager merges clean worker commits only after reviewing handoffs; any conflict or implementation correction returns to a worker. Re-pin dependent dispatches after integration.

## Human Gates

No new input is needed within accepted scope. Escalate only scope expansion or actions outside remediation, including deployment and changing installed skills. Existing authorization is retained. Unanswered questions never authorize a new irreversible action.

## Recovery And Takeover

Each ticket has a 90-minute budget and records assignment, branch, base, worktree, latest commit, evidence and next action in its issue. A silent or failed assignment is inspected before takeover; preserve its commits and history. Available slots: three workers plus this manager.

## Validation Evidence

Frozen implementation revision: `df3908e568b12f10abb3182027f9c6f1a35d4699`. Independent tester /root/ci reports all six acceptance packages pass; detailed evidence is posted to [PR #16](https://github.com/AlfaBlok/epicspine-skill/pull/16).

- Python 3.10.17 and 3.14.0: `python -B -m unittest discover -s tests -v` — 34/34 pass on each.
- Example, v1/v2 fixtures and coordination spine: separate `--strict --graph` runs — all OK. Manager also personally ran strict example/spine/fixture validation successfully.
- README install snippet in a temporary child HOME: all nine skill files copied byte-identically; a second install exits 1 and preserves an existing customized tree.
- README/example local links resolve; exact documented commands succeed.
- [GitHub push matrix](https://github.com/AlfaBlok/epicspine-skill/actions/runs/33997806296) and [PR matrix](https://github.com/AlfaBlok/epicspine-skill/actions/runs/33997807966) pass on Python 3.10 and 3.14.

The original nine-test baseline passed despite the audit gaps. The former unconditional v2 warnings are resolved by #11; strict v1 validation now passes. The final coordination-only reconciliation is validated separately without changing the tested implementation.

Residual limits: validation checks recorded structure and uses keyword heuristics for some prose contracts; it does not prove execution or verify remote issue existence. Contract sections require one contiguous pipe-led Markdown table. The original checkout and installed skill remain unchanged; PR merge and installed-skill rollout are separate steps.

## Handoff Journal

### 2026-09-06 — manager bootstrap

Created six issues and isolated manager integration worktree. User explicitly requested subagents and no manager implementation. No existing open issues, PRs or root spine were present.

## Open Questions

None requiring user input. Implementation choices remain bounded by ticket acceptance.

## Appendix

### Dispatch contract v1

Use EpicSpine. Identity: ticket worker. Bound spine: this document (read-only). Spine steward: /root. Bound issue and assignment: corresponding Issue Ledger row. First create the assigned separate worktree from the manager-pinned SHA; never switch the shared checkout. Mission and write scope: the assigned issue. Terminal state: committed tested result ready for review, or precise blocker sent to manager. Post detailed issue progress and final commit/commands/results. Do not merge main, deploy, update installed skills or change scope. No manager implementation. Go.

### 2026-09-06 — first wave dispatched

/root/parser owns #10, /root/workflow owns #13 and /root/ci owns #15, each pinned to 88c3c0cf3cff02bc36a8c11234a27f2a7450a0c5. Dependent tickets #11, #12 and #14 remain queued.

### 2026-09-06 — first wave integrated

Integrated #10 (16 tests), #13 (scoped docs review), and #15 (hosted Python 3.10/3.14 pass). #11 assigned to /root/parser on codex/audit-dialect at 0381c809ed7a704c04dadb4fb7cd50344e15ac41. /root/ci independently reviews workflow without editing it. #12 and #14 remain dependency-queued.

### 2026-09-06 — dialect integrated

#11 integrated at 0df5e291a2c069b864f1a91201dfe6ffcb7b3e40 with 26 tests passing and strict graph validation of this spine passing in the worker check. #12 dispatched to /root/parser at that SHA. #13 reviewer findings were fixed in b1ce6d2 and independently resolved. /root/ci now reviews #11; #14 remains queued behind #12.

### 2026-09-06 — validator repairs integrated, onboarding dispatched

#12 and #11 discovery correction integrated at d6a6d026430bab11430986a9258f85844564f8b4; worker reports 34 tests passing. #14 assigned to /root/workflow on codex/audit-onboarding at that SHA. /root/ci reviews the last validator changes before final combined verification. All six tickets have now been dispatched.

### 2026-09-06 — independent acceptance complete

All six issue packages pass at df3908e. Reviewer findings were routed to subagents and fixed before acceptance. Manager corrected stale coordination branch/base pointers and validation text; no manager implementation changes were made. PR #16 is the reviewable deliverable, with issues kept open until merge.
