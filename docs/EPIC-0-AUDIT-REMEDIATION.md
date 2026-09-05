# EPIC 0: Audit remediation

Status: active
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
Last reconciled commit: e909cc8ca703854e6e7b4459c0b962a937afae38

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

- [ ] Malformed Markdown rows cannot disappear from validation; empty values cannot consume following fields.
- [ ] Explicit dialect selection preserves strict legacy compatibility and enforces the selected acceptance surface.
- [ ] Non-draft issue references and ledger statuses are checked with regressions.
- [ ] Workflow rules use bounded relevant discovery and surface-appropriate personal verification.
- [ ] A complete example and quickstart validate locally; CI runs the regression suite.
- [ ] Independent tester verifies the integrated commit; final PR and residual risks are reported.

Acceptance is the local Python CLI and documentation package. No live product exists to deploy. Browser screenshots are not evidence for this repair. This scope follows the user's authorization to remediate the audited universal-browser requirement.

## Current State

Phase: implementation
Integration target: codex/audit-remediation
Fresh base commit: e909cc8ca703854e6e7b4459c0b962a937afae38
Dispatch condition: none for parser, workflow, CI; dependencies gate the remaining tickets.
Next action: Review parser, workflow and CI worker handoffs; integrate accepted commits and re-pin dependent tickets.
Blockers: none

## Execution Cursor

Last attempted: Created six GitHub remediation issues after checking for existing open work.
Result: Issues #10–#15 cover all audit findings; no duplicates found.
Execution status: active
Waiting on: worker results
Approved work: All six remediation tickets, issue comments, isolated branches, testing and review PR creation.
Next action: Await first-wave results and dispatch dialect after parser and workflow integration.

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
| [#10](https://github.com/AlfaBlok/epicspine-skill/issues/10) | Ticket worker | /root/parser | Fix Markdown parsing so malformed rows and empty fields cannot bypass validation | active | none | codex//root/parser | e909cc8ca703854e6e7b4459c0b962a937afae38 | Issue acceptance | Audit baseline | 2026-09-06 | Await worker handoff |
| [#11](https://github.com/AlfaBlok/epicspine-skill/issues/11) | Ticket worker | audit-dialect | Separate dialect selection from strictness and add real v1/v2 compatibility fixtures | ready | #10, #13 | codex/audit-dialect | e909cc8ca703854e6e7b4459c0b962a937afae38 | Issue acceptance | Audit baseline | 2026-09-06 | Wait for dependencies |
| [#12](https://github.com/AlfaBlok/epicspine-skill/issues/12) | Ticket worker | audit-ledger | Validate non-draft issue references and ledger status vocabulary | ready | #11 | codex/audit-ledger | e909cc8ca703854e6e7b4459c0b962a937afae38 | Issue acceptance | Audit baseline | 2026-09-06 | Wait for dependencies |
| [#13](https://github.com/AlfaBlok/epicspine-skill/issues/13) | Ticket worker | /root/workflow | Scope acceptance to the delivery surface and bound reuse discovery | active | none | codex//root/workflow | e909cc8ca703854e6e7b4459c0b962a937afae38 | Issue acceptance | Audit baseline | 2026-09-06 | Await worker handoff |
| [#14](https://github.com/AlfaBlok/epicspine-skill/issues/14) | Ticket worker | audit-onboarding | Add a short installation quickstart and a completed runnable example | ready | #11, #12, #13 | codex/audit-onboarding | e909cc8ca703854e6e7b4459c0b962a937afae38 | Issue acceptance | Audit baseline | 2026-09-06 | Wait for dependencies |
| [#15](https://github.com/AlfaBlok/epicspine-skill/issues/15) | Ticket worker | /root/ci | Run validator regression tests in GitHub Actions | active | none | codex//root/ci | e909cc8ca703854e6e7b4459c0b962a937afae38 | Issue acceptance | Audit baseline | 2026-09-06 | Await worker handoff |

## Branch And Integration

Manager worktree: /Users/jordi/Documents/GitHub/epicspine-audit-manager. Worker branches are codex/audit-{ticket}; separate worktrees are required. Integration target is codex/audit-remediation, with final PR targeting main. Manager merges clean worker commits only after reviewing handoffs; any conflict or implementation correction returns to a worker. Re-pin dependent dispatches after integration.

## Human Gates

No new input is needed within accepted scope. Escalate only scope expansion or actions outside remediation, including deployment and changing installed skills. Existing authorization is retained. Unanswered questions never authorize a new irreversible action.

## Recovery And Takeover

Each ticket has a 90-minute budget and records assignment, branch, base, worktree, latest commit, evidence and next action in its issue. A silent or failed assignment is inspected before takeover; preserve its commits and history. Available slots: three workers plus this manager.

## Validation Evidence

Baseline at e909cc8: python3 -B -m unittest discover -s tests -v passes nine tests. Audit probes demonstrate malformed row skipping, empty-field swallowing and unchecked issue references. The initial coordination spine has no structural errors under --graph. Current --strict fails on unconditional v2 warnings (known #11); revalidate after dialect repair. Final validation is pending worker commits and independent review.

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
