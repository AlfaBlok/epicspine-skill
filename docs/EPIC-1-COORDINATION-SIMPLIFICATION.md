# EPIC: Compact state and trustworthy rollups

Status: active
Updated: 2026-09-06
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-1-COORDINATION-SIMPLIFICATION.md
Spine ID: epicspine-coordination-simplification
Spine Type: branch
Root spine: [Audit delivery root](EPIC-0-AUDIT-REMEDIATION.md)
Parent spine: [Audit delivery root](EPIC-0-AUDIT-REMEDIATION.md)
Additional root rationale: n/a
Spine dialect: v1
Integration branch: codex/coordination-simplification
Active spine steward: /root delivery manager
Last reconciled commit: a8522464235db77d1eaca4dc03d9556d076e6bc7

## Role Bindings

User bound /root as delivery manager on 2026-09-06. Manager owns backlog, dispatch, review, integration and state records; subagents implement all changes. Individual assignments and exact bases are recorded on issues #18–#21. Independent review follows implementation.

## Write Scope

Manager: this spine and its parent's narrow child registration/rollup. Workers: assigned issue files in separate worktrees, detailed issue progress and evidence. Public fixtures must be synthetic; private adoption evidence stays in the owning repositories. Installed skills and production are outside this delivery.

## Authority By Artifact

This spine owns public-package intent and coordination. Each issue owns ticket scope/progress; code owns implementation; exact-revision tests own validation claims. Parent rollups project execution facts only; they do not make semantic decisions.

## Spine Map

No child spines.

## Mission

Reduce duplicated current state and manual synchronization while preserving evidence, history, one steward and bounded authority. Deliver a compact state profile, explicit local/GitHub ticket backends, deterministic freshness-aware rollups and structural strict validation.

## Definition Of Done

- [x] One authoritative current-state block with compatible legacy conflict detection and a compact active profile.
- [x] Explicit GitHub and local ticket references without competing mutable ledgers.
- [ ] Deterministic direct-child rollup checks/previews, truthful freshness and authority-aware apply/proposal behavior.
- [ ] Strict validation rejects objective defects and unresolved required data; prose guidance remains advisory.
- [ ] Synthetic examples, focused regression suite, independent review and reviewable PR pass on a named revision.

## Current State

Phase: implementation
Last verified: 2026-09-06
Integration target: codex/coordination-simplification
Fresh base commit: a8522464235db77d1eaca4dc03d9556d076e6bc7

## Execution Cursor

Last attempted: Resumed after worker usage interruption; integrated #19 correction and backend implementation at 8b9502e5f86f6d27c1f47e93381d2a83162fb007; resumed #20 and dispatched #21 plus independent #20 review.
Result: Integrated 60-test suite passes. #19 duplicate-field review finding corrected. #20 saved work resumed at 398632b; candidate acceptance pending.
Execution status: active
Waiting on: #20 handoff/review and #21 implementation
Approved work: User-authorized backlog delivery through subagents, isolated branches, issue comments, reviews and PRs.
Next action: Review and integrate #20/#21 when accepted; keep consumer API changes coordinated.

## Bootstrap Map

1. This spine and the assigned issue.
2. Existing skill/epic-spine/SKILL.md, assets, validator and tests.
3. Relevant accepted prior audit tests from PR #16.
4. Synthetic adoption examples only in public package.

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-09-06 | accepted | Manager-only root | User requested delivery management and subagent implementation. | Current user instruction | User rebinds role |
| 2026-09-06 | accepted | Pinned reviewed predecessor | Use a852246 from tested PR #16; stack review on codex/audit-remediation. | PR #16 independent acceptance | Predecessor changes |
| 2026-09-06 | accepted | Shared-file serialization | #18 then #19; #20 and #21 sequence unless clean file ownership is established. | Shared parser/validator surfaces | Worker handoff proves disjointness |
| 2026-09-06 | accepted | Backward compatibility | Existing spines remain readable; ambiguous state requires explicit reconciliation. | #18 acceptance | User authorizes migration |
| 2026-09-06 | accepted | Knowledge is steward-owned | Tooling may project execution facts, never infer preferences, verdicts or permission. | #20 acceptance | No automatic expansion |

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Acceptance | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [#18](https://github.com/AlfaBlok/epicspine-skill/issues/18) | Ticket worker | /root/parser | Compact authoritative state | review | PR #16 pinned | codex/compact-state | 6f63d378e0ed8e8adffdda89039f8a0c16069909 | #18 criteria | 17b2a8 accepted; integrated 48 tests pass | 2026-09-06 | PR #22 review |
| [#19](https://github.com/AlfaBlok/epicspine-skill/issues/19) | Ticket worker | /root/parser | Explicit ticket backends | review | #18 candidate pinned; review pending | codex/ticket-backends | 6512dce8c202ff9bc79730adc2f83ec8e5835ddd | #19 criteria | 54c44e1 accepted; integrated 60 tests pass | 2026-09-06 | PR #22 review |
| [#20](https://github.com/AlfaBlok/epicspine-skill/issues/20) | Ticket worker | /root/parser | Freshness-aware rollups | active | #19 candidate pinned; review pending | codex/execution-rollups | 89b3c1477a2419281c5733f7e3e7cbccf4e0e620 | #20 criteria | Resumed saved work; /root/ci reviewer | 2026-09-06 | Review handoff |
| [#21](https://github.com/AlfaBlok/epicspine-skill/issues/21) | Ticket worker | /root/workflow | Structural strictness | active | #18, #19 accepted | codex/structural-validation | 54c44e163190857264198153ba725b5c4365d932 | #21 criteria | Isolated dispatch; validator ownership | 2026-09-06 | Review handoff |

## Branch And Integration

Manager checkout: /Users/jordi/Documents/GitHub/epicspine-simplification-manager. Integration branch codex/coordination-simplification is stacked on codex/audit-remediation. Each implementation worker uses a distinct worktree from its pinned base. Manager merges reviewed commits; conflicts and fixes return to workers. Original checkouts remain untouched.

## Human Gates

No new input needed for scoped implementation/review. Main merges, production operations, external communications and installed-skill rollout are not part of this review delivery. Existing live repository tasks retain their working state; adoption work prepares isolated changes and records stale-source conflicts rather than overwriting them.

## Recovery And Takeover

Each issue records exact owner, base, worktree, latest commit, checks, blocker and next action. Budget: 90 minutes per bounded ticket, with a status/options handoff at expiry. Preserve earlier commits before takeover.

## Validation Evidence

Baseline: PR #16 has independent 34-test passes on Python 3.10 and 3.14, strict example/fixture/spine validation, and hosted CI. #18 integrated at fe91d3be962c6a0087097c364ae083a0d1f52ac4: 48 tests and strict manager graph pass after independent review corrections. #19/#20 acceptance pending.

## Handoff Journal

### 2026-09-06 — manager activation

Bound by user to deliver the simplification backlog through subagents. Rechecked dependencies and active work. Public coordination contains only generic package changes; private repository implementation is tracked on its own issues.

## Open Questions

None blocking the first wave. Contract choices remain bounded by issue acceptance; conflicting source state is evidence to reconcile, not permission to guess.

## Appendix

Dispatch contract: role ticket worker; this spine read-only; bound issue defines scope; exact base and branch recorded at assignment; dedicated writable checkout; post progress and final tested SHA to issue; manager integrates and independent reviewer verifies. No implementation by manager. Go.

### 2026-09-06 — resumed delivery

#19 integrated at 8b9502e5f86f6d27c1f47e93381d2a83162fb007; 60 tests pass. Reused existing workers after usage interruption. #20 owns new rollup files; #21 owns validator diagnostics and explicit no-blocker compatibility.
