# EPIC-9: Vertical packs: add-ons that give a repo typed sections for its function (social first)

Spine profile: compact
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-9-VERTICAL-PACKS.md
Spine ID: vertical-packs-add-ons-that-give-a-repo-typed-sections-for-its-function-social-first
Root spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Parent spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main
Integration policy: main-direct

## Goal

A repo opts into a vertical pack with one AGENTS.md line (`EpicSpine packs: social`) and gets typed content files for its function (schema, item lifecycle, who may write which transition), a validator in the commit hook, `pack init`, a JSON export the console reads as its one typed source, and wake text per persona; goals, asks and learnings stay in the normal spine. The social pack is the first; the mechanism is generic. Design: [social team deck v3](https://github.com/AlfaBlok/agent_team/blob/main/docs/plans/social-team-mvp/index.html) slides 3-6, 17.

## Serves

[EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md): the operating system extends to a repo's function without a separate spine type, so the console can skin a vertical (social.alpha9.io) on contracts instead of ad-hoc parsers; built for agent_team [EPIC-34](https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-34-social-team-mvp.md).

## Done means

- [ ] E9-1 Pack mechanism: `skill/epic-spine/packs/<name>/` (schema, validator, wake text, init), opt-in line read by the hooks; a repo without it is unchanged (tests)
- [ ] E9-2 Social pack: 7 files (brief, directions week/month, topics, ideas with from, posts with messages/feedback, assets, reports), statuses idea→draft→scheduled→posted→measured (+held, pulled, expired), writer table incl. the desk's 6-kind intake text
- [ ] E9-3 Enforcement: pre_commit blocks a malformed new item or illegal transition in a pack repo; `pack init social` scaffolds; `pack.py social --json` exports (with computed used-by / carried-by), documented in docs/doctrine/console-contract.md
- [ ] E9-4 zenod-social passes with the pack on and agent_team's console reads only the export (agent_team EPIC-34 E34-S4, S5)

## Current State

Owner: Delivery manager
Status: ready
Last attempted: scaffolded with spine_new.py on 2026-10-27
Result: created, not started
Evidence: EPIC-0-OPERATING-SYSTEM.md
Waiting on: none
Approved work: none
Next action: E9-S1 pack mechanism + social schema (agent_team EPIC-34 E34-S1 points here)
Source revision: uncommitted scaffold
Verified at: 2026-10-27

## Non-Goals

A separate spine type. Console screens (agent_team EPIC-34). Packs other than social until one is asked for.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| E9-S1 | Ticket worker | seat pool | Pack mechanism (packs/<name>/, opt-in line, hook discovery) + social pack schema and writer table | ready | none | none | main | none | 2026-10-27 | dispatch (agent_team EPIC-34 DM) |
| E9-S2 | Ticket worker | seat pool | Social pack validator in pre_commit (link, disclosure, never-say, caps, hold rules, illegal transitions) + `pack init social` | ready | E9-S1 | none | main | none | 2026-10-27 | dispatch (agent_team EPIC-34 DM) |
| E9-S3 | Ticket worker | seat pool | `pack.py social --json` export + console-contract.md section | ready | E9-S1 | none | main | none | 2026-10-27 | dispatch (agent_team EPIC-34 DM) |
| E9-S4 | Ticket worker | seat pool | Desk intake wake text (6 kinds) and per-persona wake text in the pack | ready | E9-S1 | none | main | none | 2026-10-27 | dispatch (agent_team EPIC-34 DM) |
| E9-S5 | Ticket worker | seat pool | Release: skill version bump, zenod-social turned on (agent_team E34-S4) passes | ready | E9-S2, E9-S3 | none | main | none | 2026-10-27 | dispatch (agent_team EPIC-34 DM) |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-27 | accepted | Jordi (C4): a small vertical add-on to epic-spine for the social repo's typed sections; 'let's build it' = ready | packs, not a social-epic-spine | [agent_team EPIC-34](https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-34-social-team-mvp.md) Decisions | never |
| 2026-10-27 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
