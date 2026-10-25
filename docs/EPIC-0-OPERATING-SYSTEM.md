# EPIC-0: EpicSpine operating system

Spine profile: compact
Ticket backend: github
Spine dialect: v1
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-0-OPERATING-SYSTEM.md
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
Last attempted: 2026-10-24 root DM wake (run_53683ac3): EPIC-3 closed; ledger made honest; root trimmed 141→99; `spines.py --bind` shipped (2026.10.24.8); DOD-1..3 ticked; Outcome written
Result: all three Done means met; awaiting Jordi's verification of the Outcome
Evidence: 259ed38, 89554d8, a61f07b, 85a86fd; [evidence page](root/dod-evidence-2026-10-24.md)
Waiting on: none
Approved work: none open beyond this root's DOD
Next action: Jordi verifies Outcomes of EPIC-0, EPIC-6, EPIC-7; EPIC-5 E5-5/E5-6 wait on infra-vps/zenod-social spines (Needs Jordi nj_b310a5d1)
Source revision: main
Verified at: 2026-10-25

## Mission

Make EpicSpine the lean, automatic-default common ground for agent-assisted work and the living memory of a repository. A cold agent should bind fast, read little, and act correctly. A repository's spines form one tree of goals (the epic log): each goal states its purpose and is measurably accomplishable, and the delivery manager keeps the tree and the Book coherent.

## Non-Goals

Not a product or runtime; not a general issue tracker; do not restate the skill's behaviors here (see its Default Behaviors card). EPIC-1 and EPIC-2 keep their own content and history.

## Operating Learnings

**Always** (every task; read in full at bind):

- L-1 | any task | Keep everything lean: shortest correct text/code; delete before adding | user core value | confirmed 2026-10-09
- L-2 | any task | Delivery manager coordinates and never implements; dispatch workers | user doctrine | confirmed 2026-10-09
- L-3 | dispatching | Workers, reviewers and researchers use the machine profile `~/.agents/epicspine-profile.md` (native subagent, Sonnet 5.5); never pick another model unless the user asks; independence comes from fresh context | user profile change 2026-10-10 | confirmed 2026-10-10
- L-4 | integrating | Stay in main; manager merges verified work ff-only, tests in main, reverts on red | user should never merge | confirmed 2026-10-09
- L-5 | HTML output | Serve on http://127.0.0.1:<port>/ and report that link, never a file path | clickable, recognised | confirmed 2026-10-09
- L-6 | binding | First reply names role and `Learnings in force:`; propose new learnings sparingly | user wants quick bind | confirmed 2026-10-09
- L-7 | skill changes | Regenerate MANIFEST.sha256; main is public and deployed continuously | CI enforces manifest | confirmed 2026-10-09
- L-8 | any task | Hygiene is routine: remove worktree and branch right after integrating | disk cost; user won't manage | confirmed 2026-10-09
- L-9 | planning/dispatch | Resolve open decisions before dispatch: the agent settles facts itself by reading the repo and running commands, the user makes decisions; record each resolved decision in the spine's Decisions table, and ask only real forks one at a time with a recommendation | user approved comparison adoption | confirmed 2026-10-09
- L-10 | dispatch | Launch only the ready frontier: tickets whose Depends On blockers are done and whose write surfaces are disjoint from every in-flight worker; sequence the rest | user approved comparison adoption | confirmed 2026-10-09
- L-11 | reviewing | Verify worker output on two independent axes—repo standards (tests, validators, conventions, lean) and the spec (the ticket's acceptance)—against the repository and diff, never from the worker's summary | user approved comparison adoption | confirmed 2026-10-09
- L-12 | integrating | `main-direct` is the default for every repo; PR/CI only for the declared `Deploy gate:` paths/workflows/branches whose push to main rolls a complex production deployment (e.g. zenod), never the whole repo; docs-only, additive and research changes stay main-direct | user doctrine 2026-10-16 | confirmed 2026-10-16
- L-13 | any task | The delivery manager keeps the epic tree and the Book coherent: every new ask is placed in the tree (an existing goal, or a new leaf under the right parent) before work starts; at every launch, dispatch and record it resolves contradictions and writes the reasoning (Decisions) and current state | user doctrine 2026-10-19 | confirmed 2026-10-19
- L-14 | doctrine | epicspine-skill owns the EpicSpine doctrine and orchestrates it from here; agent_team complies when its console reads repos; each repo applies the doctrine to its own spines in its own thread; learn what we are trying to accomplish here | Jordi 2026-10-19 | confirmed 2026-10-19
- L-18 | any session | Never show other repos' state inside a session about one repo unless the conversation is explicitly about them; the background checker does its job and records, it never broadcasts machine-wide notices to every session | user 2026-10-24 | confirmed 2026-10-24
- L-19 | branch hygiene | Parked work gets out of the way: archive it (annotated tag `archive/<name>`, pushed and verified), delete the branch, never remind or ask about it again; non-destructive cleanup needs no question | user 2026-10-24 | confirmed 2026-10-24
- L-20 | reporting a repo "on latest" | "On latest EpicSpine" means installed AND conforming (`spines.py --json`: 0 orphans, 0 mismatches, each `looks_like_epic` page a coded epic or recorded exception), never just the skill or block version; proof is the [conformance table](epic-log/conformance.md) | EPIC-3 E3-5, Jordi 2026-10-19 (handoff step 7) | confirmed 2026-10-24

**Scoped index**: none yet.

## Definition Of Done

- [x] DOD-1 A cold agent binds in three hops (AGENTS.md → this root spine → the branch matching its task), reading ≲ 100 lines before acting. (2026-10-24: `spines.py --bind`, skill 2026.10.24.8, merge 85a86fd; fresh agent 61 spine lines, was 282: [evidence](root/dod-evidence-2026-10-24.md))
- [x] DOD-2 The lean SKILL.md kernel and its Default Behaviors card are landed and installed copies re-synced. (2026-10-24: [evidence](root/dod-evidence-2026-10-24.md), SKILL.md 72 lines, manifest match, seat1/seat2 link to the checkout)
- [x] DOD-3 Strict graph validation and `python3 -B -m unittest discover -s tests` are green on main. (2026-10-24: 655 tests OK; `validate_spine.py --strict --graph docs/EPIC-*.md` 0 errors after EPIC-3 Decisions fix)

## Outcome

Verdict: accomplished
Outcome: EpicSpine is a lean, always-on default: a cold agent binds with one `spines.py --bind` call (61 lines read, was 282), the 72-line SKILL.md kernel and Default Behaviors card ship with every installed copy linked to the canonical checkout, and 656 tests plus strict graph validation are green on main.
Closed: 2026-10-24 by run_53683ac3-ba33-4027-ad9c-251e9144e36f
Risk: the fresh-agent bind was measured once (n=1) on Claude; the thin repo-block template still says "read Current State and Operating Learnings" (the live global block, which outranks it, says `--bind`); Gemini cold start untested.

| Done means | Evidence |
|---|---|
| DOD-1 | 85a86fd (skill 2026.10.24.8, `spines.py --bind`), [evidence](root/dod-evidence-2026-10-24.md): 61 lines |
| DOD-2 | d85992f evidence page: SKILL.md 72 lines, manifest match, seat1/seat2 linked |
| DOD-3 | 85a86fd: unittest OK (2 skipped), `validate_spine.py --strict --graph docs/EPIC-*.md` 0 errors |

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker (Opus 5.5, T3 thread) | Enforce manager-never-implements and push-on-close with hooks: PreToolUse `manager_guard.py` (allowlist-first Bash/Edit policy, subagents via `agent_id`) + Stop `push_gate.py` | deferred | none | PR #28 (feat/manager-guards) | 6ccb101 | PARKED 2026-10-13 by user (D18); archived 2026-10-24 as tags `archive/feat/manager-guards`, `archive/feat/dispatcher-guard` (branches deleted, PR #28 closed). Do not merge, install, or build on it | 2026-10-24 | none (parked: not raised again) |

Done tickets (39 rows, Next Action done/none, moved verbatim): [done ledger](root/steps.md#done-ledger).

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|

21 decisions: [decisions table](root/decisions.md#decisions-table).

## EpicSpine Book Companion

Status: active
Book root: index.html
Book steward: /root delivery manager

Binding rule, validation command and the remaining fields: [book-companion](root/book-companion.md).

## Spine Map

| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |
|---|---|---|---|---|---|---|---|---|
| epicspine-audit-remediation | child | [EPIC-2 Audit remediation](EPIC-2-AUDIT-REMEDIATION.md) | Audit remediation delivery | done | none | PR #16 | 2026-10-09 | Reference only; reopen if scope resumes |
| epicspine-coordination-simplification | child | [EPIC-1 Coordination simplification](EPIC-1-COORDINATION-SIMPLIFICATION.md) | Compact state and trustworthy rollups | done | none | PR #22 | 2026-10-09 | Reference only; reopen if scope resumes |
| epicspine-epic-log | child | [EPIC-3 Epic log](EPIC-3-EPIC-LOG.md) | Contributes the epic log: every goal in the 16 repos hangs in one tree from a root (0 orphans, 0 mismatches) and "on latest" means installed and conforming (Outcome: accomplished) | done | none | Outcome 2026-10-24; [conformance](epic-log/conformance.md) | 2026-10-24 | Reference only; reopen if scope resumes |
| epicspine-doctrine-2 | child | [EPIC-4 Doctrine 2 semantic goal tree](EPIC-4-DOCTRINE-2.md) | Contributes the human layer: every epic now says what it achieves and why, how it serves its parent and what each child adds, and the agent_team console shows it (Outcome: accomplished) | done | none | Outcome 2026-10-22; skill 2026.10.22.5 | 2026-10-22 | Reference only; reopen if scope resumes |
| persona-files-and-standing-spines | child | [EPIC-5: Persona files and standing spines](EPIC-5-PERSONA-AND-STANDING-SPINES.md) | doctrine for persona markdown files and for standing (never-closing, target-per-period) spines, so the console and any repo read teams the same way | active | none | E5-1..E5-4 met; merges 1d4e9fc, 1acbdde | 2026-10-24 | infra-vps/zenod-social adopt (E5-5, E5-6) |
| status-true-spines-the-checker-catches-what-makes-the-console-status-lie | child | [EPIC-6: Status-true spines: the checker catches what makes the console status lie](EPIC-6-STATUS-TRUE-SPINES.md) | contributes the checks the agent_team console status model (agent_team EPIC-13) depends on: free-text asks, done with open Done means, contradictory Waiting on | review | none | Outcome 2026-10-24, merge 44ab11e | 2026-10-24 | Jordi verifies Outcome |
| runnable-epics-run-state-contract | child | [EPIC-7: Runnable epics: run_state contract](EPIC-7-RUNNABLE-EPICS.md) | Defines which epics a wake may run (run_state/runnable/has_children from the Status they already carry), so a Delivery Manager never works finished or planning epics. | active | none | branch e14-s1 (not merged), skill 2026.10.24.9, 691 tests OK | 2026-10-24 | DM verifies and merges e14-s1; then roll out to other machines |
| closed-epics-close-their-rows-tree-audit | child | [EPIC-8: Closed epics close their rows; tree audit](EPIC-8-CLOSED-EPICS-CLOSE-ROWS.md) | A finished epic shows no open work, and any repo's stale tree can be audited and swept from the skill. | active | none | branch wt/e16-s1-close-rows (not merged), skill 2026.10.24.10, 715 tests OK | 2026-10-24 | DM verifies and merges; then roll out (E8-3) |
