# EPIC-5: Persona files and standing spines

Spine profile: compact
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-5-PERSONA-AND-STANDING-SPINES.md
Spine ID: persona-files-and-standing-spines
Root spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Parent spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main
Integration policy: main-direct

## Goal

EpicSpine defines how a persona is written as a markdown file and how a standing spine (ongoing work with targets per period, never closed) is written, so the agent_team console and any repo read teams the same way

## Serves

[EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md): teams of personas become part of the doctrine, like spines: readable by any tool, installable in any repo

## Done means

- [ ] E5-1 Persona file format in references: generic only (frontmatter: name, template, model, host; body: Remit, Reads, Writes), no goal, cadence or write scope in it. What a persona does for a goal (cadence, write scope, goal-specific instructions) is the assignment, written in that epic's `## Team` table (persona, cadence, write scope, notes). A persona is not an epic; several personas work one epic (agent_team L-20). Validator + `spines.py --json` (or a sibling) lists a repo's personas and each epic's team.
- [ ] E5-2 Standing spine kind: `## Targets` (target per period) and a Current State scoreboard (target vs actual for this period); a miss becomes a ledger row; never needs an Outcome; the validator accepts it.
- [ ] E5-3 Tasks and hand-offs: a task is an Issue Ledger row with an assignee (Owner column) and a status; every persona wake starts with its queue (open rows assigned to it in the epics it is on); hand-off = reassign the row (several rows for several jobs); a task serving another goal goes in that goal's ledger with a link back; a task that outgrows a wake or two becomes a child epic. Every action is a commit signed by the persona; shared files keep a fixed shape; each section has a named writer via the assignment's write scope.
- [ ] E5-4 Assignees must exist: the validator rejects a ledger row whose assignee is not a persona on that repo's team (persona files in the repo, or the epic's `## Team` table until files exist) or `Jordi`; `spines.py --json` lists each persona's queue.
- [ ] E5-5 Asks as tasks: an ask to Jordi is a ledger row assigned to `Jordi` (same fields as an ask: what, why, impact, risk + rollback, recommendation); tried first on infra-vps EPIC-15, then adopted or dropped with a Decisions row.
- [ ] E5-6 Used for real: zenod-social and infra-vps EPIC-15 spines and their persona files validate, with every ledger assignee a real persona or Jordi.

## Current State

Owner: Delivery Manager (agent-team console)
Status: active
Last attempted: 2026-10-24 DM wake run_aa2dd0a3: dispatched E5-S1 (run_9a0d7ebe, branch e5-s1) and E5-S3 (run_c76affed, main-direct)
Result: 2 workers running; E5-S2 sequenced after E5-S1 (both edit validate_spine.py, L-10)
Evidence: EPIC-0-OPERATING-SYSTEM.md
Waiting on: nobody
Approved work: none
Next action: verify and merge E5-S1, land E5-S3, then dispatch E5-S2; agent_team EPIC-11, zenod-social and infra-vps EPIC-15 wait on the format
Source revision: main
Verified at: 2026-10-24

## Non-Goals

Console UI (agent_team EPIC-11). Changing finish-line spines.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| E5-S1 | Ticket worker | worker run_9a0d7ebe (Sonnet 5.5, seat1) | persona file format + validator + listing | active | none | e5-s1 | main | none | 2026-10-24 | dispatch |
| E5-S2 | Ticket worker | unassigned | standing spine kind + scoreboard + validator | ready | E5-S1 (shared validator) | none | main | none | 2026-10-24 | dispatch |
| E5-S3 | Ticket worker | worker run_c76affed (Sonnet 5.5, seat1) | writing contract for personas sharing a repo | active | none | main | main | none | 2026-10-24 | dispatch |
| E5-S4 | Ticket worker | unassigned | validator accepts step codes (E5-S1) as Issue in row-as-ticket spines: spine_new.py scaffolds fail --strict | ready | E5-S1 (shared validator) | none | main | `validate_spine.py --strict` on this spine: 3 ES-S-TICKET errors (pre-existing) | 2026-10-24 | dispatch after E5-S1 merges |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |
| 2026-10-24 | accepted | Requested by agent_team EPIC-12 (approved plan): EpicSpine owns the persona and standing-spine formats; the console only reads them | format owner = doctrine owner (agent_team L-12) | [agent_team EPIC-12](https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-12-zenod-live-heard-sold.md) | never |
| 2026-10-24 | accepted | Persona generic, assignment (cadence, write scope, goal notes) in the epic's Team table; tasks = ledger rows with an assignee that must be a real persona or Jordi; asks-as-tasks trialled on infra-vps EPIC-15 | Jordi 2026-10-24 ('go for it'; 'you cannot make an owner that is not a persona in the repo') | [agent_team EPIC-12](https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-12-zenod-live-heard-sold.md) | after the EPIC-15 trial |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
