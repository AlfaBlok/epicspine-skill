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

- [x] E9-1 Pack mechanism: `skill/epic-spine/packs/<name>/` (schema, validator, wake text, init), opt-in line read by the hooks; a repo without it is unchanged (tests) (7c8b7bb/3ae4843; tests/test_packs.py; 788 tests OK 2026-10-28)
- [x] E9-2 Social pack: 7 files (brief, directions week/month, topics, ideas with from, posts with messages/feedback, assets, reports), statuses idea→draft→scheduled→posted→measured (+held, pulled, expired), writer table incl. the desk's 6-kind intake text (packs/social/schema.json (7c8b7bb), 6 intake kinds 774f12e)
- [x] E9-3 Enforcement: pre_commit blocks a malformed new item or illegal transition in a pack repo; `pack init social` scaffolds; `pack.py social --json` exports (with computed used-by / carried-by), documented in docs/doctrine/console-contract.md (validator+init 9acd869, export 6f54429, docs/doctrine/console-contract.md 'Pack data')
- [x] E9-4 zenod-social passes with the pack on and agent_team's console reads only the export (agent_team EPIC-34 E34-S4, S5) (2026-11-02: zenod-social `pack.py validate` ok; agent_team E34-S5 done: merge 3240e53, console serves /api/tenants/:id/social from the pack export, 3 parsers deleted, live check passed)

## Current State

Owner: Delivery Manager (agent-team console)
Status: review
Last attempted: 2026-11-02 DM wake run_3f8ab8a1: E9-4 met (agent_team E34-S5 deployed and live-checked); Outcome written
Result: all four Done means met; awaiting Jordi's verdict
Evidence: merges 3ae4843, 6f54429, 9acd869, 70d34d9, d0da7c1; agent_team 3240e53
Waiting on: nobody
Approved work: none
Next action: Jordi marks the verdict (console Mark accomplished)
Source revision: main
Verified at: 2026-11-02

## Outcome

Outcome: A repo turns on a vertical pack with one AGENTS.md line (`Pack: social`) and gets typed content files, a commit-hook validator for items and status moves, `pack init`, desk and per-persona wake text, and a JSON export that agent_team's console now reads as its only typed source for zenod-social.
Risk: one pack (social) and one repo (zenod-social) so far; the export contract (`schemaVersion` 1) binds the console, so a breaking schema change needs a version bump; zenod-social has no reports yet (1 export warning).

| Done means | Evidence |
|---|---|
| E9-1 | 7c8b7bb, merge 3ae4843 (release 2026.10.27.1); tests/test_packs.py |
| E9-2 | packs/social/schema.json (7c8b7bb); 6 intake kinds 774f12e |
| E9-3 | validator + init 9acd869; export 6f54429; docs/doctrine/console-contract.md "Pack data"; per-persona wake text d0da7c1 |
| E9-4 | zenod-social `pack.py validate` ok 2026-11-02; agent_team E34-S5 merge 3240e53, go-live evidence |

## Non-Goals

A separate spine type. Console screens (agent_team EPIC-34). Packs other than social until one is asked for.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| E9-S1 | Ticket worker | seat pool | Pack mechanism (packs/<name>/, opt-in line, hook discovery) + social pack schema and writer table | done | none | merged 3ae4843 | main | 7c8b7bb, merge 3ae4843 (E34-S1, release 2026.10.27.1) | 2026-10-28 | none |
| E9-S2 | Ticket worker | seat pool | Social pack validator in pre_commit (link, disclosure, never-say, caps, hold rules, illegal transitions) + `pack init social` | done | E9-S1 | merged 9acd869 | main | b665398, merge 9acd869 (E34-S2); E34-S4 fixes ab1ced4 | 2026-10-28 | none |
| E9-S3 | Ticket worker | seat pool | `pack.py social --json` export + console-contract.md section | done | E9-S1 | merged 6f54429 | main | f0d861f, merge 6f54429 (E34-S3); console-contract.md 'Pack data' | 2026-10-28 | none |
| E9-S4 | Ticket worker | worker run_4ce95ec6 (Sonnet 5.5, seat1) | Desk intake wake text (6 kinds) and per-persona wake text in the pack | done | E9-S1 | merged (branch deleted) | desk 774f12e; per-persona d851e3a, merge d0da7c1 (release 2026.10.28.1); 794 tests OK | desk intake 774f12e, merge 70d34d9 (E34-S10); per-persona `--wake-text --role` d851e3a (release 2026.10.28.1) | none | DM verifies and merges
| E9-S5 | Ticket worker | seat pool | Release: skill version bump, zenod-social turned on (agent_team E34-S4) passes | done | E9-S2, E9-S3 | main | main | releases 2026.10.27.1-.7; zenod-social `Pack: social`, `pack.py validate` ok, export 42 posts / 1 warning (2026-10-28) | 2026-10-28 | none |
| E9-S6 | Delivery manager | Delivery Manager | E9-4: console reads only the pack export (agent_team E34-S5 deployed) | done | none | main | main | agent_team 3240e53 (E34-S5, evidence/e34-s5, go-live evidence/e34-golive) | 2026-11-02 | none |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-27 | accepted | Jordi (C4): a small vertical add-on to epic-spine for the social repo's typed sections; 'let's build it' = ready | packs, not a social-epic-spine | [agent_team EPIC-34](https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-34-social-team-mvp.md) Decisions | never |
| 2026-10-27 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |
| 2026-11-07 | accepted | Social pack release 2026.11.07.2 (fee7d83): the posts ledger's optional Benefit column moved last, after Status, so ledgers and fixtures read by position keep their Status; made by agent_team E71-S2's worker (run_5adf6738) when the console tests refused feedback writes on 2026.11.07.1. The commit named no row; attributed here by agent_team E63-S16 | an optional pack column goes after Status | fee7d83, CHANGELOG 2026.11.07.2, agent_team docs/spines/benefits-as-the-totem-of-the-social-oper.md E71-S2 | never |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
