# EPIC: EpicSpine operating system

Spine profile: compact
Ticket backend: github
Spine dialect: v1
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-2-OPERATING-SYSTEM.md
Spine ID: epicspine-operating-system
Spine Type: root
Root spine: self
Parent spine: none
Additional root rationale: n/a
Integration branch: main
Integration policy: main-direct
Dispatch profile: default
Skill updates: auto

## Current State

Owner: /root delivery manager
Status: active
Last attempted: 2026-10-09 landed roles+dispatch profile, git doctrine, operating learnings, hygiene sweep, skill self-update and freshness.
Result: repo self-managed; CI green on main at 5a9241c.
Evidence: [main @ 5a9241c](https://github.com/AlfaBlok/epicspine-skill/commit/5a9241c) and [CI runs](https://github.com/AlfaBlok/epicspine-skill/actions)
Waiting on: none
Approved work: lean SKILL.md kernel, then re-sync installed copies of the skill.
Next action: land the lean SKILL.md kernel + Default Behaviors card + CI line budgets in wt/kernel, then re-sync installed copies.
Source revision: 5a9241c
Verified at: 2026-10-09
Last sweep: 2026-10-09, main clean
EpicSpine skill: 2026.10.09 @ 5a9241c, checked 2026-10-09

## Mission

Make EpicSpine the lean, automatic-default common ground for agent-assisted work and the living memory of a repository. A cold agent should bind fast, read little, and act correctly.

## Non-Goals

Not a product or runtime; not a general issue tracker; do not restate the skill's behaviors here (see its Default Behaviors card). EPIC-0 and EPIC-1 keep their own content and history.

## Operating Learnings

**Always** (every task; read in full at bind):

- L-1 | any task | Keep everything lean: shortest correct text/code; delete before adding | user core value | confirmed 2026-10-09
- L-2 | any task | Delivery manager coordinates and never implements; dispatch workers | user doctrine | confirmed 2026-10-09
- L-3 | dispatching | Default workers, reviewers and researchers: T3 delegate_task, OpenCode opencode-go/deepseek-v4.1-flash, reasoning high; never pick another model unless the user asks; independence comes from fresh context | user rule; manager broke it 2026-10-09 | confirmed 2026-10-09
- L-4 | integrating | Stay in main; manager merges verified work ff-only, tests in main, reverts on red | user should never merge | confirmed 2026-10-09
- L-5 | HTML output | Serve on http://127.0.0.1:<port>/ and report that link, never a file path | clickable, recognised | confirmed 2026-10-09
- L-6 | binding | First reply names role and `Learnings in force:`; propose new learnings sparingly | user wants quick bind | confirmed 2026-10-09
- L-7 | skill changes | Regenerate MANIFEST.sha256; main is public and deployed continuously | CI enforces manifest | confirmed 2026-10-09
- L-8 | any task | Hygiene is routine: remove worktree and branch right after integrating | disk cost; user won't manage | confirmed 2026-10-09

**Scoped index**: none yet.

## Definition Of Done

- [ ] A cold agent binds in three hops (AGENTS.md → this root spine → the branch matching its task), reading ≲ 100 lines before acting.
- [ ] The lean SKILL.md kernel and its Default Behaviors card are landed and installed copies re-synced.
- [ ] Strict graph validation and `python3 -B -m unittest discover -s tests` are green on main.

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | /root/kernel | Lean SKILL.md kernel + Default Behaviors card + CI line budgets | draft | none | wt/kernel | 5a9241c | in flight | 2026-10-09 | integrate when green |
| draft | Ticket worker | /root delivery manager | Re-sync installed copies of the skill | draft | kernel | wt/sync | main | not started | 2026-10-09 | dispatch after kernel lands |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-09 | accepted | Two base roles | Every agent is a delivery manager or a worker; older identities are remits under them. | user decision 2026-10-09 | Role model changes |
| 2026-10-09 | accepted | Stay in main, manager merges | Workers use local wt/<task> worktrees; the manager merges verified work to main. | user decision 2026-10-09 | User asks for PR review |
| 2026-10-09 | accepted | Learnings tree | Root Always list plus a scoped index; depth is scope. | user decision 2026-10-09 | Learning model changes |
| 2026-10-09 | accepted | Sweep as a worker brief | Hygiene is a dispatched brief, not a third base role. | user decision 2026-10-09 | Sweep needs its own role |
| 2026-10-09 | accepted | Skill updates auto | `Skill updates: auto` is the default; upgrade between tasks. | user decision 2026-10-09 | User prefers manual |
| 2026-10-09 | accepted | EPIC-0 and EPIC-1 closed | Both prior epics are done children of this root; their content is preserved. | user decision 2026-10-09 | Delivery scope resumes |
| 2026-10-09 | accepted | Root wiring | This compact spine is the single root; EPIC-0 and EPIC-1 are its direct children. | user decision 2026-10-09 | Hierarchy needs re-scoping |
| 2026-10-09 | accepted | No unrequested model changes | Every subagent, reviewers included, uses the default profile unless the user asks; fresh context gives review independence. | user decision 2026-10-09 | User names another model |

## Spine Map

| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |
|---|---|---|---|---|---|---|---|---|
| epicspine-audit-remediation | child | [EPIC-0 Audit remediation](EPIC-0-AUDIT-REMEDIATION.md) | Audit remediation delivery | done | none | PR #16 | 2026-10-09 | Reference only; reopen if scope resumes |
| epicspine-coordination-simplification | child | [EPIC-1 Coordination simplification](EPIC-1-COORDINATION-SIMPLIFICATION.md) | Compact state and trustworthy rollups | done | none | PR #22 | 2026-10-09 | Reference only; reopen if scope resumes |
