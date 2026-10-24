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

- [ ] E5-1 Persona file format in references (frontmatter: name, template, assigned epic(s) — a persona is not an epic, several personas work one epic (agent_team L-20) —, cadence, model, host, may-write; body: Remit, Reads, Writes) with a validator, and `spines.py --json` (or a sibling) lists a repo's personas.
- [ ] E5-2 Standing spine kind: `## Targets` (target per period) and a Current State scoreboard (target vs actual for this period); a miss becomes a ledger row; never needs an Outcome; the validator accepts it.
- [ ] E5-3 Writing contract for personas sharing one epic: every action a commit signed by the persona, shared files with a fixed shape, hand-offs as ledger rows whose status says whose turn it is.
- [ ] E5-4 Used for real: zenod-social root spine + its persona files validate.

## Current State

Owner: EPIC-5 manager (bind on dispatch)
Status: ready
Last attempted: scaffolded with spine_new.py on 2026-10-24
Result: created, not started
Evidence: EPIC-0-OPERATING-SYSTEM.md
Waiting on: nobody
Approved work: none
Next action: draft E5-1..E5-3 in references; agent_team EPIC-11 and zenod-social wait on the format
Source revision: uncommitted scaffold
Verified at: 2026-10-24

## Non-Goals

Console UI (agent_team EPIC-11). Changing finish-line spines.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| E5-S1 | Ticket worker | unassigned | persona file format + validator + listing | ready | none | none | main | none | 2026-10-24 | dispatch |
| E5-S2 | Ticket worker | unassigned | standing spine kind + scoreboard + validator | ready | none | none | main | none | 2026-10-24 | dispatch |
| E5-S3 | Ticket worker | unassigned | writing contract for personas sharing a repo | ready | none | none | main | none | 2026-10-24 | dispatch |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |
| 2026-10-24 | accepted | Requested by agent_team EPIC-12 (approved plan): EpicSpine owns the persona and standing-spine formats; the console only reads them | format owner = doctrine owner (agent_team L-12) | [agent_team EPIC-12](https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-12-zenod-live-heard-sold.md) | never |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
