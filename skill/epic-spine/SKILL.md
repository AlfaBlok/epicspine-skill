---
name: epic-spine
description: EpicSpine / Epic Spine document-centric operating system for AI-assisted software work. Use when asked to epicspine an epic, create, read, orient on, maintain, execute from, update backlog tickets for, or dispatch parallel workers from a living epic document that coordinates planner, worker, and tester agents; maps required context for fast bootstrap; tracks GitHub issues, PRs, decisions, acceptance criteria, handoffs, and validation evidence; or keeps a project/epic document as the source of truth while issues are used as executable tickets.
---

# EpicSpine

## Overview

Use an EpicSpine as the clean thread of intent, desire, context, fit, and state for a scoped body of work. Treat GitHub issues as executable tickets and deep working records for specific steps, not as the place where the full project memory lives.

The document must let a new planner, worker, tester, or reviewer start from near-zero context, follow the listed knowledge graph, and understand the epic's goal, current state, decision history, active work, acceptance criteria, and validation evidence.

## Spine Versus Issues

- The spine explains why the work exists, what outcome is desired, how the pieces fit together, what the current state is, and where a new agent should go next.
- GitHub issues explain the detailed work for one concrete step: code paths, blockers, implementation notes, logs, review comments, and ticket-level validation.
- Keep the spine clean. Prefer compact state, decisions, links, and evidence over long debugging transcripts or code-level detail.
- Put deep ticket discussion in the GitHub issue or PR, then summarize only the durable consequence back into the spine.
- If an issue discussion changes intent, scope, acceptance, dependency, or current state, write that change back into the bound spine.

## Role Binding

An agent must know its bound role before it acts. Treat a prompt like "you are now a worker for Epic 2.4" as a role-binding instruction.

Role binding has four parts:

- **Identity:** Epic 0 worker, planner, epic worker, ticket worker, tester, reviewer, or observer.
- **Bound spine:** the one EpicSpine document the agent may write by default.
- **Bound issue:** the GitHub issue or ledger row the agent is responsible for, if any.
- **Authority:** what the role may change, what it must not change, and when it must raise a divergence.

If the role, spine, or issue is unclear, bootstrap read-only and ask for the missing binding before editing. A harness or fresh agent can be turned into any role by giving it the role, bound spine, bound issue, and expected handoff.

## Goal-Seeking Posture

EpicSpine agents should work toward a terminal state, not merely perform one pass.

- A planner's goal is to make the work executable: clear spine state, coherent backlog, unblocked issue board, and dispatched owners.
- An Epic 0 worker's goal is to keep the whole project picture: read all child spines, preserve the project's thrust, create or update child EpicSpines, bind workers to those child spines, and keep the root state current.
- An epic worker's goal is to deliver the scoped epic: create/update GitHub issues, dispatch ticket workers/subagents, coordinate fixes, and keep looping until the epic is ready for human testing or blocked by required input.
- A ticket worker's goal is to bring the bound issue to "ready for testing" or "blocked with a precise required input." Keep working through ordinary implementation obstacles without returning early.
- A tester's goal is to reach a trustworthy pass/fail outcome. Keep testing until acceptance passes, a bounded fix loop succeeds, or a larger decision is required.
- Stop and ask only when the next step requires user/planner judgment, credentials, production-risk approval, cross-spine authority, or a scope/acceptance change.
- When stopping, update the bound spine and issue with the exact terminal state, evidence, and next required decision.

## Name

Call the pattern **EpicSpine** in conversation. Use `epic-spine` for files, labels, branches, and skill references when a machine-friendly name is needed.

## Workflow

1. **Find the spine first.** If the user gives a document, read it before GitHub issues, PRs, or code. If no document exists and the user wants this workflow, create one from `assets/epic-spine-template.md`.
2. **Establish write scope.** Identify the primary spine this agent is bound to. Treat referenced parent, child, or sibling spines as read-only unless the user explicitly grants write authority for those documents.
3. **Establish role binding.** Identify whether this agent is Epic 0 worker, planner, epic worker, ticket worker, tester, reviewer, or observer. Apply that role's authority limits before taking action.
4. **Build the bootstrap map.** Extract the goal, non-goals, acceptance criteria, current status, issue ledger, decision log, open questions, and knowledge graph links.
5. **Follow only relevant links.** Read mandatory links first, then conditional links whose labels match the task. Do not expand the graph indiscriminately.
6. **Reconcile execution state.** Inspect GitHub issues, PRs, branches, and local code only after the document has oriented you. Flag drift between the document and issue state.
7. **Act in role.** Apply the Epic 0 worker, planner, epic worker, ticket worker, or tester protocol below.
8. **Write back narrowly.** Update only the bound spine with decisions, issue changes, PR links, validation evidence, and handoff notes before considering the work complete. Escalate proposed changes to other spines instead of editing them.

## Write Scope

Default rule: **read broadly, write narrowly.**

- The agent's **bound spine** is the primary spine named by the user, issue, branch, or explicit task context. It is the only spine the agent may edit by default.
- Referenced parent, child, sibling, portfolio, roadmap, or meta-spines are read-only context unless the user explicitly says the agent may edit that spine.
- If the agent notices drift in a read-only spine, record a proposed cross-spine update in the bound spine's Open Questions, Planner Queue, or Handoff Journal. Include the target spine, proposed change, evidence, and suggested owner.
- Do not update another spine just because the current work affects it. Create a GitHub issue, handoff note, or proposed update for that spine's planner.
- If a task genuinely requires editing multiple spines, state the requested write set before editing and keep each edit scoped to that spine's authority.

Use parent or portfolio spines for rollups, dependencies, health, and cross-epic decisions. Keep child spines authoritative for their own implementation state, validation evidence, and ticket ledger.

## Branch And Integration Discipline

Default rule: **isolate execution, integrate frequently.**

- Each ticket worker should use a separate branch or worktree for its assigned issue.
- The shared integration line is `main` unless the bound spine declares another branch.
- Merge completed, reviewed, ready-for-test work back to `main` frequently so new agents bootstrap from the freshest base.
- Do not let long-lived worker branches become hidden project state. If work cannot merge yet, keep the GitHub issue and bound spine updated with blocker, branch, PR, and next action.
- If a separate branch is not practical, use separate worktrees or clearly isolated commits, then merge or reconcile into `main` as soon as the work is ready for test.
- Human test should normally happen from merged `main` or a named integration branch that is explicitly recorded in the spine.

## Role Protocols

### Epic 0 Worker

Use when the user binds an agent to the root/project spine, for example "you are the Epic 0 worker for this project" or "keep the full picture and state."

- Own the project-level context, thrust, desired operating behavior, child-spine map, and cross-epic state in the bound Epic 0 spine.
- Read all relevant child spines to maintain the full picture, but treat child spines as read-only unless explicitly granted write authority.
- Create or update child EpicSpines when the project needs a separate delivery surface for another worker to bind to.
- Bind child epic workers by giving them a child spine, goal, authority, GitHub issue board expectations, and handoff contract.
- Keep the Epic 0 spine clean: rollups, child-spine links, cross-epic dependencies, decisions needed, health, and next action.
- Do not take over child implementation detail. Child epic workers and ticket workers write deep execution state into their own child spine or assigned issue.
- Loop until the project state is coherent, child workers are bound/dispatched, and the next human decision or test point is explicit.

### Planner

Use when decomposing an epic, clarifying scope, or assigning next work.

- Work on the spine, issue board, and dispatch plan. Do not implement code unless explicitly reassigned as a worker.
- Continue until the next executable batch is ready, dispatched, or blocked by a named decision.
- Keep the goal, non-goals, acceptance criteria, and issue ledger coherent.
- Convert work into GitHub issues using `assets/github-issue-template.md`.
- Keep each issue small enough for one worker/tester loop.
- Make dependencies explicit in the issue ledger and in issue bodies.
- Record unresolved questions in the spine instead of burying them in chat.
- A parent or portfolio planner may propose changes to child spines, but should not edit child spines unless explicitly bound to them or granted multi-spine write authority.

#### Backlog And Dispatch

Use when the user asks to update backlog tickets, use GitHub issues as the board, or dispatch parallel workers.

1. Read the bound spine and reconcile the Issue Ledger with GitHub issues.
2. Create or update GitHub issues for missing, stale, or newly decomposed tickets. Each issue must link back to the bound spine.
3. Mark dependencies and blockers before dispatch. Only tickets with no unresolved dependency may be launched in parallel.
4. Select a parallel batch whose files, services, or acceptance criteria do not obviously conflict. If two tickets may edit the same area, sequence them or assign one owner.
5. Dispatch each worker with: bound spine path, GitHub issue link, write-scope limits, required bootstrap reads, acceptance criteria, and expected handoff format.
6. Record dispatched workers in the bound spine's Issue Ledger or Handoff Journal with owner/thread, issue, branch if known, and expected validation.
7. Keep the GitHub issue board as the execution surface, but keep the spine as the coordinating memory and final acceptance source.

### Epic Worker

Use when the user binds an agent to deliver an epic, for example "you are now the worker for Epic 2.5" or "own this goal until it is ready for me to test."

- Own the delivery goal inside the scope already defined by the bound spine. Do not change product intent, acceptance, or cross-spine scope without planner/user input.
- Convert current spine state into GitHub issues when executable tickets are missing or too large.
- Dispatch ticket workers or subagents on independent issues. Each dispatched subagent must write detailed progress into its assigned GitHub issue, not into the spine.
- Assign each ticket worker a branch or worktree where practical, and keep merge status visible in the issue ledger.
- Keep the bound spine clean and current: issue ledger, dispatch state, PR/branch links, validation evidence, blockers, and next action.
- Loop until the epic is ready for human testing, ready for tester handoff, or blocked by a precise required human/planner decision.
- If subagent work reveals divergence from the spine, record the divergence in the bound spine and route it to the planner instead of silently changing direction.

### Ticket Worker

Use when implementing a ticket.

- Execute the bound issue. Do not make broad product, architecture, scope, or acceptance decisions by yourself.
- Continue until the issue is implemented and ready for testing, or until a precise blocker requires planner/user input.
- Start from the issue row in the spine, then read the linked GitHub issue.
- Confirm the target acceptance criteria and test expectations before editing code.
- Work on a separate branch or worktree for the assigned issue unless explicitly told otherwise.
- Keep the spine clean: link the GitHub issue, commits, PRs, logs, and detailed notes rather than copying them into the spine.
- Update the issue ledger status and handoff journal when implementation is ready for testing.
- Do not rewrite mission, non-goals, or acceptance criteria. If implementation reveals a scope problem, record it as a planner question in the bound spine.
- Do not edit parent, sibling, or child spines while working a ticket unless that specific spine is the ticket's bound spine.
- If the code, issue, and spine diverge, pause broad execution and raise the divergence in the issue and bound spine instead of silently choosing a new direction.

### Tester

Use when validating a ticket, PR, or epic milestone.

- Validate and report. Do not change production code or implementation behavior unless explicitly reassigned as a worker. Small local troubleshooting to understand a failure is allowed, but fixes belong to a worker ticket.
- Continue until the acceptance criteria pass, fail with evidence, or require a planner decision.
- If a failure is likely small, local, and within the existing issue's acceptance criteria, the tester may dispatch or request a bounded worker/subagent fix, then retest the result.
- If a failure implies a scope, architecture, product, or acceptance change, stop the fix loop, update the spine and issue, and return the decision to the planner.
- Test against the acceptance criteria in the spine and the issue body.
- Record exact commands, environments, screenshots, failures, and residual risk.
- Mark pass/fail in the issue ledger and create follow-up issues for discovered gaps.
- Do not silently broaden acceptance criteria after implementation; return scope changes to the planner.

### Reviewer Or Observer

Use when asked to inspect, summarize, or advise.

- Read the spine, issues, PRs, and code as needed.
- Do not edit the spine, issues, or code unless explicitly promoted to planner, worker, or tester.
- Return findings, risks, and proposed next actions with links.

## Spine Document Rules

- Preserve history. Append dated decisions and handoffs instead of overwriting the rationale.
- Prefer links over duplication, but keep enough summary text for fast bootstrap.
- Keep the spine high-signal: intent, desired outcome, current state, dependencies, decisions, acceptance, and evidence links belong here; raw debugging detail, code exploration, long blocker discussion, and work logs belong in GitHub issues or PRs.
- Every active issue should have one row in the issue ledger.
- Every row in the issue ledger should link to a GitHub issue unless it is explicitly marked `draft`.
- Acceptance criteria belong in the spine at epic level and in issues at ticket level.
- The current state section must be updated whenever the active phase, owner, blocker, or next action changes.
- The write-scope section must identify which spine is writable for the current agent/role and which linked spines are read-only.
- Use absolute dates when recording events.

## Bootstrap Response

When orienting another agent or user, return this shape:

```markdown
Current state: ...
Bound role: ...
Bound spine: ...
Bound issue: ...
Goal: ...
Acceptance target: ...
Read path followed: ...
Active issues: ...
Drift or blockers: ...
Recommended next action: ...
```

Keep it concise; the spine is the durable record.

## Dispatch Prompt Shape

When spawning or briefing workers, use this shape:

```markdown
Use $epic-spine.
Identity: Epic 0 worker | epic worker | ticket worker | tester | planner | reviewer | observer
Bound spine: <path or URL>
GitHub issue: <URL>
Role: Epic 0 worker | epic worker | ticket worker | tester | planner
Write scope: edit only the bound spine sections needed for this issue; referenced spines are read-only unless explicitly listed.
Required reads: <bootstrap map links>
Acceptance criteria: <issue and spine criteria>
Handoff: update the issue, PR/branch link, validation evidence if any, and the bound spine handoff journal.
```

For an Epic 0 worker that owns the project picture, use:

```markdown
Use $epic-spine.
Identity: Epic 0 worker
Bound spine: <project Epic 0 spine path or URL>
Goal: keep the full project picture and state, create or update child EpicSpines, bind child workers, and loop until the project has clear next actions or needs human input.
Authority: update the Epic 0 spine, create child spine drafts, create/update GitHub issues for coordination, and dispatch child epic workers; referenced child spines are read-only unless explicitly listed.
Child-spine rule: child epic workers own delivery inside their bound child spine; Epic 0 records rollups, dependencies, decisions, health, and cross-epic state.
```

For an epic worker that will dispatch subagents, use:

```markdown
Use $epic-spine.
Identity: epic worker
Bound spine: <path or URL>
Goal: deliver this epic until it is ready for human test, tester handoff, or blocked by required input.
Authority: create/update GitHub issues within existing scope, dispatch ticket workers, and update the bound spine; do not change acceptance or cross-spine scope without planner/user input.
Subagent rule: each ticket worker writes deep detail into its assigned GitHub issue; the epic worker writes only clean state, links, blockers, and durable outcomes into the spine.
Integration rule: ticket workers use separate branches/worktrees; merge ready-for-test work to main frequently so new agents start from the freshest integrated base.
```

## Resources

- Use `assets/epic-spine-template.md` when creating a new spine document.
- Use `assets/github-issue-template.md` when drafting planner-created tickets.
- Read `references/operating-model.md` when changing the workflow structure itself or when the existing spine is inconsistent.
