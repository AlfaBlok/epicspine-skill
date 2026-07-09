# EPIC: <name>

Status: draft
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Repository: <owner/repo or path>
Primary document: <link or path to this file>
GitHub issues: <owner/repo/issues or "same repository">
Integration branch: main
Planner: <name or agent/thread>
Worker: <name or agent/thread>
Tester: <name or agent/thread>

## Role Bindings

| Identity | Bound Issue / Scope | Authority | Handoff |
|---|---|---|---|
| Epic 0 worker | <project/root scope> | Maintain project state, child-spine map, rollups, dependencies, dispatch notes; create child spine drafts. | Root spine current, child workers bound, next human decision clear. |
| Planner | <epic scope> | Edit this spine's planning sections and GitHub issue board; do not implement code by default. | Updated issue ledger, decisions, dispatch notes. |
| Epic worker | <epic scope> | Create/update GitHub issues within existing scope, dispatch ticket workers, update this spine's delivery state. | Spine issue ledger, dispatch state, blockers, ready-for-test state. |
| Ticket worker | <issue URL or ledger row> | Execute assigned issue; update issue and limited spine status/evidence/handoff. | PR/branch, implementation notes in issue, spine handoff. |
| Tester | <issue URL, PR, or milestone> | Validate against acceptance; update validation evidence and pass/fail. | Test commands, result, risks, follow-up issues. |
| Reviewer | <scope> | Read and report findings; no mutation unless promoted. | Findings and proposed next actions. |

## Write Scope

Bound spine: <this document>
Writable by default:

- <planner role or thread>
- <worker role or thread, limited to assigned issue status/evidence/handoff>
- <tester role or thread, limited to validation evidence/status>

Read-only linked spines:

- <parent, child, sibling, portfolio, or roadmap spine>

Cross-spine change rule: read linked spines for context, but record proposed edits here unless explicitly granted write authority for the target spine.

## Mission

State the outcome in one paragraph. Write for a capable teammate who has not seen the chat history.

## Definition Of Done

- [ ] <observable final acceptance criterion>
- [ ] <observable final acceptance criterion>
- [ ] <required validation or release criterion>

## Non-Goals

- <explicitly out of scope>

## Current State

Phase: planning | implementation | testing | blocked | complete
Last verified: YYYY-MM-DD
Next action: <single next action>
Blockers: <none or list>

## Role Goals

| Identity | Goal | Terminal State |
|---|---|---|
| Epic 0 worker | Keep the full project picture and child-spine system coherent. | Child spines mapped, state rolled up, workers bound, or human decision required. |
| Planner | Make the work executable and dispatched. | Backlog ready/dispatched or named blocker. |
| Epic worker | Deliver the scoped epic through GitHub issue/subagent loop. | Ready for human test, tester handoff, or blocked with required input. |
| Ticket worker | Complete the bound issue. | Ready for testing or blocked with required input. |
| Tester | Prove pass/fail. | Acceptance passed, evidenced failure, or planner decision required. |

## Bootstrap Map

Read in this order:

| Priority | Link | Why It Matters | When To Read |
|---|---|---|---|
| 1 | <path or URL> | <core context> | Always |
| 2 | <path or URL> | <implementation context> | Worker |
| 3 | <path or URL> | <test context> | Tester |

## Architecture And Context

Summarize the system pieces, constraints, and vocabulary needed to work on this epic.

Keep this section high-signal. Link to GitHub issues, PRs, commits, logs, and deeper notes instead of copying ticket-level detail here.

## Decisions

| Date | Decision | Rationale | Evidence |
|---|---|---|---|
| YYYY-MM-DD | <decision> | <why> | <link> |

## Issue Ledger

| Issue | Role | Title | Status | Depends On | PR/Branch | Acceptance | Latest Evidence | Next Action |
|---|---|---|---|---|---|---|---|---|
| draft | Planner | <ticket title> | draft | - | - | <ticket acceptance> | - | <next action> |

## Branch And Integration

- Default integration branch: `main`
- Worker isolation: one ticket worker per branch or worktree by default.
- Ready-for-test rule: merge completed work to the integration branch frequently so new agents bootstrap from the freshest base.
- If not merged, the issue ledger must show branch/PR, blocker, owner, and next action.

## Planner Queue

- <planning item or question>

## Worker Queue

- <implementation item>

## Tester Queue

- <validation item>

## Validation Evidence

| Date | Scope | Command / Method | Result | Evidence |
|---|---|---|---|---|
| YYYY-MM-DD | <issue or milestone> | `<command>` | pass/fail | <link or note> |

## Handoff Journal

### YYYY-MM-DD - <role> - <summary>

Context:
Next:
Risks:
Links:

## Open Questions

- <question> Owner: <owner>. Needed by: <date or phase>.

## Proposed Cross-Spine Updates

| Date | Target Spine | Proposed Change | Evidence | Suggested Owner | Status |
|---|---|---|---|---|---|
| YYYY-MM-DD | <path or URL> | <summary> | <link> | <owner> | proposed |

## Appendix

Add lower-priority links, raw notes, or source material that should not interrupt fast bootstrap.
