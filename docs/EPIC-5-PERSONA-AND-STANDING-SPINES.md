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

- [x] E5-1 Persona file format in references: generic only (frontmatter: name, template, model, host; body: Remit, Reads, Writes), no goal, cadence or write scope in it. What a persona does for a goal (cadence, write scope, goal-specific instructions) is the assignment, written in that epic's `## Team` table (persona, cadence, write scope, notes). A persona is not an epic; several personas work one epic (agent_team L-20). Validator + `spines.py --json` (or a sibling) lists a repo's personas and each epic's team. (2026-10-24: references/personas.md, personas.py; merge 1d4e9fc)
- [x] E5-2 Standing spine kind: `## Targets` (target per period) and a Current State scoreboard (target vs actual for this period); a miss becomes a ledger row; never needs an Outcome; the validator accepts it. (2026-10-24: references/standing-spines.md, standing.py; merge 1acbdde)
- [x] E5-3 Tasks and hand-offs: a task is an Issue Ledger row with an assignee (Owner column) and a status; every persona wake starts with its queue (open rows assigned to it in the epics it is on); hand-off = reassign the row (several rows for several jobs); a task serving another goal goes in that goal's ledger with a link back; a task that outgrows a wake or two becomes a child epic. Every action is a commit signed by the persona; shared files keep a fixed shape; each section has a named writer via the assignment's write scope. (2026-10-24: references/persona-tasks.md, 69372e6)
- [x] E5-4 Assignees must exist: the validator rejects a ledger row whose assignee is not a persona on that repo's team (persona files in the repo, or the epic's `## Team` table until files exist) or `Jordi`; `spines.py --json` lists each persona's queue. (2026-10-24: personas.assignee_errors + spines.py --json personas/queue; merge 1d4e9fc)
- [x] E5-5 Asks as tasks: an ask to Jordi is a ledger row assigned to `Jordi` (same fields as an ask: what, why, impact, risk + rollback, recommendation); tried first on infra-vps EPIC-15, then adopted or dropped with a Decisions row. (2026-11-11: dropped as doctrine, Decisions row; asks stay coded `[ask]` lines under `## Waiting on`)
- [ ] E5-6 Used for real: zenod-social and infra-vps EPIC-15 spines and their persona files validate, with every ledger assignee a real persona or Jordi.

## Current State

Owner: Delivery Manager (agent-team console)
Status: active
Last attempted: 2026-11-14 DM wake run_3becf441: re-validated: infra-vps EPIC-15 --strict OK (f50dbc8), persona files OK in both repos; zenod-social root 4 errors (292d364); desk note 909a983; E5-S7 worker run_494cef71 started (claim-aware assignee check)
Result: E5-1..E5-5 met; E5-6 half met: infra-vps EPIC-15 and all persona files --strict OK; checker now accepts claim.py lease owners (eeb73d6); zenod-social root 3 errors on 2 of its rows
Evidence: infra-vps f50dbc8 (5bb1480 fix), zenod-social 292d364 validated 2026-11-14; desk notes 909a983 (zenod-social), 88ade64 (infra-vps reply closed)
Waiting on: nobody
Monitoring: zenod-social root strict-clean since 2026-11-11 until 2026-11-21 · next check 2026-11-16T08:00Z re-validate (desk note 909a983) · then tick E5-6, write the Outcome, Status review
Approved work: none
Next action: zenod-social fixes 2 rows (L-14, desk note 909a983); re-validate on its reply or 2026-11-16; tick E5-6 when it passes, then Outcome and Status review
Source revision: main
Verified at: 2026-11-14

## Waiting on

- [answered EPIC-5-A2 2026-11-11 @Delivery-Manager] Should an ask to Jordi be a ledger row assigned to him (the infra-vps trial) instead of a coded ask line? — answer: no, dropped; asks stay one coded line under Waiting on, a row may still name Jordi as its owner while it waits — why: only infra-vps used rows, and the console's cards, FYIs and duplicate guard all read the coded lines, so two forms split one inbox — rollback: reopen E5-5 and delete its Decisions row

- [answered EPIC-5-A1 2026-10-26 @Unblocker · done 2026-10-27 infra-vps a465c42, zenod-social 19f0de9 (Jordi approved nj_958bad5c)] May the epicspine-skill Delivery Manager add persona files to infra-vps and zenod-social so EPIC-5 can finish? (console Needs Jordi nj_958bad5c, raised 2026-10-25 by the Delivery Manager, row E5-6) — answer: yes, as proposed: new `personas/<name>.md` files only, one per persona already on infra-vps EPIC-15's and zenod-social root's Team tables, copied from the console persona; change no existing file; run `validate_spine.py --strict` on the files and both spines and revert the repo's commit if either fails; one commit per repo, main-direct — why: E5-6 Done means requires persona files in both repos; Jordi approved the same kind of cross-repo, reversible, docs-only edit for this same row on 2026-10-25 (nj_b310a5d1, done in 9409eb5 and 4c72143); new files grant no access, spend nothing and publish nothing — source: EPIC-5 Done means E5-6; Jordi's approve of nj_b310a5d1 (2026-10-25); E5-1 persona format (references/personas.md) — confidence: 80% — rollback: `git revert` the one commit in each repo (or delete the new personas/ files); the Team tables stay the assignee source until files exist (E5-4)

## Non-Goals

Console UI (agent_team EPIC-11). Changing finish-line spines.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| E5-S1 | Ticket worker | worker run_9a0d7ebe-08f5-4cc1-a847-1108f1f784c1 | persona file format + validator + listing | done | none | merged (branch deleted) | main | 633052c (674 tests OK; references/personas.md); DM verified: 674 tests OK, manifest match | 2026-10-24 | none |
| E5-S2 | Ticket worker | worker run_86cb23c5-5c72-4444-b558-72eeb0120c6f | standing spine kind + scoreboard + validator | done | none | merged (branch deleted) | main | 721bfda, merge 1acbdde; DM verified 694 OK, graph --strict 0 | 2026-10-24 | none |
| E5-S3 | Ticket worker | worker run_c76affed (Sonnet 5.5, seat1) | writing contract for personas sharing a repo | done | none | main | main | 69372e6, 4c10634: references/persona-tasks.md; DM verified 660 tests OK, manifest match | 2026-10-24 | none |
| E5-S4 | Ticket worker | worker run_98fc838e (with E6-S1) | validator accepts step codes (E5-S1) as Issue in row-as-ticket spines: spine_new.py scaffolds fail --strict | done | none | merged (branch deleted) | main | c804f48, merge 44ab11e; graph --strict 0 errors | 2026-10-24 | none |
| E5-S5 | Ticket worker | worker run_83cd4392 | Jordi on a Team table needs no persona file | done | none | merged (branch deleted) | main | 89a1521, merge 085cf62; 730 tests OK | 2026-10-26 | none |
| E5-S6 | Ticket worker | worker run_c14d5ebb (Sonnet 5.5, seat2) | persona files are not orphan pages (pre-commit flagged all 8 in infra-vps a465c42, zenod-social 19f0de9) | done | none | merged (branch deleted) | main | 4a19298, merge 8461a2c (release 2026.10.27.4; version renumbered from .3, collided with the pack release); 775 tests OK | 2026-10-27 | none |
| E5-S7 | Delivery manager | Delivery Manager | E5-6: infra-vps EPIC-15 and zenod-social spines + persona files strict-clean | active | zenod-social root: 2 rows of its own (a Decisions row above the separator, E0-S63 worker owner; L-14, desk note 909a983) | main | main | 2026-11-14: infra-vps EPIC-15 --strict OK (f50dbc8); claim-aware assignee check eeb73d6 (run_494cef71, 920 tests OK, E0-S53 error gone); zenod-social 14→3 (292d364); desk note 909a983 | 2026-11-14 | re-validate zenod-social on its reply or 2026-11-16; tick E5-6 when it passes |
| E5-S8 | Ticket worker | unassigned | assignee check skips finished rows: a done or superseded row is nobody's queue, so its historic worker assignee is not an error (9 of zenod-social's and 1 of infra-vps' strict errors) | done (no confirm: validator plumbing, its effect shows as fewer errors on other repos' spines) | none | main | main | personas.assignee_errors skips finished rows via claim.CLOSED (done/superseded/cancelled/moved), open rows stay checked; code + test landed in 72e37ce (swept in by the DM spine commit, 2026.11.11.2), old test updated in the E5-S8 commit; 915 tests OK; --strict: zenod-social root 21 → 14 errors (assignee 10 → 3, left: E0-S29 active, E0-S52 and E0-S59 review), infra-vps EPIC-15 14 → 13 (assignee 1 → 0); EPIC-0 --graph output unchanged | 2026-11-11 | none: E5-S7 desk-notes the remaining errors |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |
| 2026-10-24 | accepted | Requested by agent_team EPIC-12 (approved plan): EpicSpine owns the persona and standing-spine formats; the console only reads them | format owner = doctrine owner (agent_team L-12) | [agent_team EPIC-12](https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-12-zenod-live-heard-sold.md) | never |
| 2026-10-24 | accepted | Persona generic, assignment (cadence, write scope, goal notes) in the epic's Team table; tasks = ledger rows with an assignee that must be a real persona or Jordi; asks-as-tasks trialled on infra-vps EPIC-15 | Jordi 2026-10-24 ('go for it'; 'you cannot make an owner that is not a persona in the repo') | [agent_team EPIC-12](https://github.com/AlfaBlok/agent_team/blob/main/docs/spines/epic-12-zenod-live-heard-sold.md) | after the EPIC-15 trial |
| 2026-10-26 | accepted | decided by Unblocker: EPIC-5-A1 (nj_958bad5c) yes, DM may add new persona files to infra-vps and zenod-social, validate --strict, one commit per repo | E5-6 needs them; same scope as Jordi's approved nj_b310a5d1; additive and reversible | Waiting on EPIC-5-A1; run_7983789d | rollback: git revert the commit in each repo |
| 2026-11-11 | accepted | decided by Delivery Manager: E5-5 asks-as-tasks dropped as doctrine — why: after 2.5 weeks only infra-vps used it (E15-R13, E15-S1) while the console made the coded `[ask CODE]` line under `## Waiting on` the one place Jordi answers (cards, FYIs, duplicate guard); two forms of the same ask split his inbox — rollback: reopen E5-5 and revert this row | asks stay coded lines; a row may still name `Jordi` as Owner while it waits on his ask (E5-4 accepts it) | infra-vps EPIC-15 Decisions 2026-10-24, hand-off table; run_905a0cea | Jordi reverses the FYI EPIC-5-A2 |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
