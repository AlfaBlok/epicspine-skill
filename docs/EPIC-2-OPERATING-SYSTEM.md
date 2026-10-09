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
Last attempted: 2026-10-09 comparison adoption complete: L-9..L-11 landed (a868281), P2 test rewritten (a694ae2), post-adoption smoke 4/4; tagged checkpoint/post-adoption. Prior: cold-start test passed on the default worker: a fresh agent bound via AGENTS.md -> root spine -> SKILL.md, named the default profile, and found the Default Behaviors card.
Result: all four agreed steps landed; main at e48e6fd; 120 tests, agents_block check, strict validation, manifest and skill status all green.
Evidence: [main @ e48e6fd](https://github.com/AlfaBlok/epicspine-skill/commit/e48e6fd) and [CI runs](https://github.com/AlfaBlok/epicspine-skill/actions)
Waiting on: none
Approved work: none.
Next action: idle; reopen the ledger to start new work.
Source revision: e48e6fd
Verified at: 2026-10-09
Last sweep: 2026-10-09, main clean
EpicSpine skill: 2026.10.09 @ 6e827e8; installed hub fresh, checked 2026-10-09

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
- L-9 | planning/dispatch | Resolve open decisions before dispatch: the agent settles facts itself by reading the repo and running commands, the user makes decisions; record each resolved decision in the spine's Decisions table, and ask only real forks one at a time with a recommendation | user approved comparison adoption | confirmed 2026-10-09
- L-10 | dispatch | Launch only the ready frontier: tickets whose Depends On blockers are done and whose write surfaces are disjoint from every in-flight worker; sequence the rest | user approved comparison adoption | confirmed 2026-10-09
- L-11 | reviewing | Verify worker output on two independent axes—repo standards (tests, validators, conventions, lean) and the spec (the ticket's acceptance)—against the repository and diff, never from the worker's summary | user approved comparison adoption | confirmed 2026-10-09

**Scoped index**: none yet.

## Definition Of Done

- [ ] A cold agent binds in three hops (AGENTS.md → this root spine → the branch matching its task), reading ≲ 100 lines before acting.
- [ ] The lean SKILL.md kernel and its Default Behaviors card are landed and installed copies re-synced.
- [ ] Strict graph validation and `python3 -B -m unittest discover -s tests` are green on main.

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | /root delivery manager | Always-on AGENTS.md block + installer + CI check | draft | none | wt/agents-block | 1993233 | integrated on 02d7a88; 115 tests + block + manifest green; worktree removed | 2026-10-09 | done |
| draft | Ticket worker | /root/kernel (thread 441c3c64) | Lean SKILL.md kernel + Default Behaviors card + CI line budgets | draft | none | wt/kernel | main | integrated on d547410; 120 tests + agents_block check + strict validate + manifest green | 2026-10-09 | done |
| draft | Ticket worker | /root delivery manager | Centralize installed skill: hub + harness symlinks + pin SOURCE | draft | none | n/a | main | ~/.agents/skills/epic-spine real copy; Claude/OpenCode/Codex symlink to it; skill_update status fresh | 2026-10-09 | done |
| draft | Ticket worker | /root delivery manager | Cold-start test: fresh agent per provider binds and dispatches | draft | none | n/a | main | passed on opencode_2/deepseek-v4.1-flash: bound as delivery manager, named the default profile, card present, no dead ends | 2026-10-09 | done |
| draft | Ticket worker | worker A (default profile) | Default-behavior contract tests + SMOKE.md baseline | draft | none | wt/behavior-tests | b620d50 | integrated on 3108192; 125 tests green; mutation check fails as intended; smoke baseline P1 pass, P2 pass, P3 provisional pass (dry run stopped at first read; tighten preamble) | 2026-10-09 | done |
| draft | Ticket worker | worker B (default profile) | Adopt L-9..L-11 doctrine + extend tests/smoke | draft | worker A | wt/adopt-l9-l11 | 3108192 | integrated on a868281 (rebased over 7d617c2); 136 tests, strict validate, block check, manifest green; smoke 4/4 after P2 test rewrite (a694ae2) | 2026-10-09 | done |
| draft | Ticket worker | worker C (default profile) | Shortlist-by-default: JSON + generated sortable/filterable HTML as the default deliverable when a shortlist is key (port from abnb_agent SHORTLIST_STANDARD, check idea_scraper) | draft | none (SKILL.md/MANIFEST merge serialized after B) | wt/shortlist-default | 5fffe5a | dispatched | 2026-10-09 | verify diff + tests + served demo URL, ff-merge after B |
| draft | Ticket worker | worker D (default profile) | Shortlist template: table-first compact layout (user feedback on demo page) | draft | worker C | wt/shortlist-table-first | a868281 | integrated (ff-only, 7781d8e); 137 tests + strict validate + agents_block + manifest green; screenshot reviewed; demo re-served 200; worktree removed; installed skill upgraded | 2026-10-09 | done |

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
| 2026-10-09 | accepted | Serialize MANIFEST-changing merges | One writer per spine and one MANIFEST merge at a time: agents-block landed first, kernel rebases second; the second merge regenerates MANIFEST. | thread collision a0380f46 vs 441c3c64 | Two branches touch MANIFEST |
| 2026-10-09 | accepted | Comparison adoption fork | Adopt L-9 (resolve decisions before dispatch), L-10 (ready frontier), L-11 (two-axis verification) in our own words from the Pocock/poteto comparison. Guarded by tags checkpoint/pre-adoption (b620d50) and checkpoint/post-adoption, plus contract tests and a dry-run smoke test. Revert = `git revert b620d50..HEAD`, then re-sync the installed skill; never reset public main. | user decision 2026-10-09; thread a0380f46 | Smoke or contract tests regress |
| 2026-10-09 | accepted | L-9 asks on missing details | L-9 stays as written: when an instruction leaves out a detail, the agent asks one clear question with a recommendation before dispatching. The P2 smoke prompt was a bad test (an unspecified typo), not a rule regression; P2 is rewritten as a fully specified edit and the ask-first behavior stays covered by P4. | user decision 2026-10-09 | Over-asking becomes a recurring complaint |

## Spine Map

| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |
|---|---|---|---|---|---|---|---|---|
| epicspine-audit-remediation | child | [EPIC-0 Audit remediation](EPIC-0-AUDIT-REMEDIATION.md) | Audit remediation delivery | done | none | PR #16 | 2026-10-09 | Reference only; reopen if scope resumes |
| epicspine-coordination-simplification | child | [EPIC-1 Coordination simplification](EPIC-1-COORDINATION-SIMPLIFICATION.md) | Compact state and trustworthy rollups | done | none | PR #22 | 2026-10-09 | Reference only; reopen if scope resumes |
