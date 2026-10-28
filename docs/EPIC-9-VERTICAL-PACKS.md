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
- [ ] E9-4 zenod-social passes with the pack on and agent_team's console reads only the export (agent_team EPIC-34 E34-S4, S5)

## Current State

Owner: Delivery Manager (agent-team console)
Status: active
Last attempted: 2026-10-28 DM wake run_8679887e: reconciled E9-S1..S3, S5 (agent_team EPIC-34 builds, verified); E9-S4 per-persona wake text merged d0da7c1 (release 2026.10.28.1)
Result: E9-1..E9-3 met; all E9 rows done; E9-4 half: zenod-social passes, console export-only read is agent_team E34-S5 (merged, deploy pending its D12)
Evidence: merges 3ae4843, 6f54429, 9acd869, 70d34d9, 6b6c56e, db83b3c
Waiting on: nobody
Approved work: none
Next action: tick E9-4 when agent_team E34-S5 is deployed; then write the Outcome and set Status review
Monitoring: agent_team E34-S5 deployed (console reads only the pack export) since 2026-10-28 · next check 2026-10-28T20:00Z agent_team epic-34 E34-S5 row · then tick E9-4, Outcome, Status review
Source revision: main
Verified at: 2026-10-28

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

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-27 | accepted | Jordi (C4): a small vertical add-on to epic-spine for the social repo's typed sections; 'let's build it' = ready | packs, not a social-epic-spine | [agent_team EPIC-34](https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-34-social-team-mvp.md) Decisions | never |
| 2026-10-27 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
