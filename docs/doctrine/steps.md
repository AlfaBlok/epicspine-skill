# Steps of EPIC-4: detail

Page of [EPIC-4](../EPIC-4-DOCTRINE-2.md). The Issue Ledger there keeps one line per step; each step's full text, as it stood in the ledger, is here. Step 10 and 11 had a stray extra cell in the ledger; their two evidence cells are joined under Latest Evidence.

## Step 1

- **Role:** Delivery manager
- **Owner / Assignment:** worker seat1 (Sonnet 5.5), task epic4-step1-doctrine-draft-r1
- **Title:** 1. Define the doctrine (coherence pass): one short page a newcomer reads, replacing skill text, not adding to it; Doctrine 2 text in plain language (what a spine must say, and why; Doctrine 1 vs 2 table; `Doctrine:` header; status words; rule: if a goal's why is not written in the repo, ask the spine's owner, never invent it) plus open ambiguities as concrete questions, one at a time, each with a recommendation, in this order (a, How to work this, dropped by Jordi: the cold-start objective is in the Goal and E4-5): (b) One switch: `Doctrine: <n>` is what a reader needs; profile and dialect become optional, one line each; `leaf` accepted as alias of `branch`. (c) Spine vs tickets: the ledger row is the ticket; a GitHub issue or local ticket file is optional, linked only when one step needs its own discussion; one concrete what-goes-where example. (d) Maintenance duties in at most 5 lines (record, close, roll up to parent, supersede, keep Current State lean), mechanics owned by EPIC-3 E3-2. (e) Glossary of at most 6 lines (Goal/Mission, Done means/DoD/Acceptance, epic/spine/goal/milestone). (f) `--strict` stays advisory; whatever Doctrine 2 requires is enforced at the trackable level or dropped. Jordi approves
- **Status:** done
- **Depends On:** none
- **PR/Branch:** merged
- **Base:** main
- **Latest Evidence:** merged 9f3b093 (wt/doctrine-2 0fabf2d, branch removed); approved EPIC-4-A1; doc/spine tests OK; SKILL.md 79->72 lines
- **Last Verified:** 2026-10-22
- **Next Action:** none

## Step 2

- **Role:** Delivery manager
- **Owner / Assignment:** EPIC-4 delivery manager
- **Title:** 2. Plan enforcement: short plan for Jordi covering scaffold (new epics follow the doctrine by default), commit check (newly added epics only), visibility (`spines --json`: `missing_sections`; discovery follows epic parent links and page inbound links (an epic has one parent, a page one or more); pages under each epic, any depth; orphan = no tree leaf links to it; status rolls up to the nearest epic ancestor; advisory "looks like an epic" flag on pages with goal markers (Goal / Done means / checkbox outcomes / Next action / Status); console), steps (Latest Evidence is the step's test), advisory size budget per epic (line count plus long-cell warnings), recording includes propagating a major finding to the parent, migration ("make it compliant" path); Jordi approves before any tool work
- **Status:** done
- **Depends On:** step 1
- **PR/Branch:** none
- **Base:** main
- **Latest Evidence:** [enforcement.md](enforcement.md) on main; approved EPIC-4-A1 2026-10-21
- **Last Verified:** 2026-10-22
- **Next Action:** none; built by step 3

## Step 3

- **Role:** Ticket worker
- **Owner / Assignment:** worker seat1 (Sonnet 5.5), task epic4-step3-tools-r1, console run run_4b6bd75d
- **Title:** 3. Tools: `spine_new` writes Doctrine 2 by default; `## Done means` accepted as the DoD heading; `spines --json` fields; commit check for new spines; template; release
- **Status:** done
- **Depends On:** step 2 (done)
- **PR/Branch:** merged
- **Base:** main
- **Latest Evidence:** released 2026.10.22.1 (merge 6be5e7c, branch removed); full isolated suite 606 OK (2 skip) on merged main; skill -3 lines; EPIC-4 --json: goal, serves, 5 done_means, 4 pages, no missing_sections
- **Last Verified:** 2026-10-22
- **Next Action:** none
- **Brief:** [tools-brief.md](tools-brief.md) (worker spec)

## Step 4

- **Role:** agent_team delivery manager
- **Owner / Assignment:** agent_team thread mcp:6734cbcd-4cab-456a-9bcc-dbff1b10f713
- **Title:** 4. Console reads Doctrine 2 from `spines --json` and shows Goal, Serves chain, children, Done means first; also verify the agent pipeline: a persona launched from the console receives the EpicSpine always-on block (SessionStart hook) and binds to its spine
- **Status:** done
- **Depends On:** contract (parallel with step 3); live check after step 3
- **PR/Branch:** none
- **Base:** main
- **Latest Evidence:** live check on 2026.10.22.1 (2026-10-22): EPIC-4 Definitions tab shows Goal, Serves chain to EPIC-0, Done means 2/5 above tickets, 3 pages, no missing_sections ([screenshot](http://100.104.206.10:18770/epic4-live-overview-2026-10-22.png)); agent_team 1a27502, ca8fc10, deploy c5f8bdb; children + contributes on EPIC-0 ([screenshot](http://100.104.206.10:18770/epic0-live-children-2026-10-22.png)); E4-3 met
- **Last Verified:** 2026-10-19
- **Next Action:** relink orphan page tools-brief.md at the step 6 merge

## Step 5

- **Role:** poly-maker delivery manager
- **Owner / Assignment:** fresh poly-maker thread
- **Title:** 5. Compliance test: "make Epic 4 compliant with the latest EpicSpine doctrine", nothing more; console shows it; success includes asking Jordi for any unwritten why; then run the E4-5 cold-start check on poly-maker E4
- **Status:** draft
- **Depends On:** step 3 shipped and skill synced to vps1 (launch); step 4 (console view)
- **PR/Branch:** none
- **Base:** main
- **Latest Evidence:** none
- **Last Verified:** 2026-10-19
- **Next Action:** launch a fresh thread in the poly-maker project (2026.10.22.1 released)

## Step 6

- **Role:** Delivery manager
- **Owner / Assignment:** EPIC-4 delivery manager
- **Title:** 6. Slim to L-17, EPIC-4 first (one-line ledger rows and Decisions, detail moved to linked pages), then run the E4-5 cold-start check on EPIC-4; then EPIC-0 (root) and EPIC-3
- **Status:** draft
- **Depends On:** step 3
- **PR/Branch:** none
- **Base:** main
- **Latest Evidence:** EPIC-4 is the first Doctrine 2 spine
- **Last Verified:** 2026-10-19
- **Next Action:** after step 3

## Step 7

- **Role:** Ticket worker
- **Owner / Assignment:** worker seat1 (Sonnet 5.5), task epic4-step7-root-swap-r1
- **Title:** 7. Root swap (L-15): EPIC-2 root becomes EPIC-0, done audit EPIC-0 becomes EPIC-2; one job: rename files, update links and headers repo-wide (docs, README, AGENTS.md `Root spine:`, examples, handoffs, explainer), and the live thread briefs that cite "EPIC-2 L-x"; history text left as is
- **Status:** done
- **Depends On:** step 1 vocabulary approved (L-16, done)
- **PR/Branch:** wt/root-swap
- **Base:** main
- **Latest Evidence:** merged and pushed: main ef15cfa (branch 336ae54); doc-reading tests pass; briefs updated by root DM (719ffe9)
- **Last Verified:** 2026-10-19
- **Next Action:** none; see step 8 for the load-failing sync tests

## Step 8

- **Role:** Delivery manager
- **Owner / Assignment:** EPIC-4 delivery manager
- **Title:** 8. Quiet re-run (also: pre-commit tests run from a linked worktree exercise main's hook, not the branch's; step 3 worker ran from a plain clone): test_background_sync, test_session_sync, test_local_mess, test_auto_return failed or timed out under load 34 after the swap (background_sync, session_sync also fail before it); re-run when the host is quiet
- **Status:** draft
- **Depends On:** quiet host
- **PR/Branch:** none
- **Base:** main
- **Latest Evidence:** ef15cfa run 2026-10-19
- **Last Verified:** 2026-10-19
- **Next Action:** re-run the 4 files; open a fix only if one fails on a quiet host

## Step 9

- **Role:** Ticket worker
- **Owner / Assignment:** native subagent (Sonnet 5.5), resumed after seat1 provider failure
- **Title:** 9. Personas must receive the doctrine: tests never touch real harness config (CLAUDE_CONFIG_DIR leak healed/stripped ~/.claude_seat1, pointer in ~/.claude aimed at a worktree); installer never targets a worktree or a config dir outside HOME, never deletes settings.json
- **Status:** done
- **Depends On:** none
- **PR/Branch:** merged
- **Base:** main
- **Latest Evidence:** released 2026.10.21.2 (merge 383ac11); isolated suite 562 OK; seat1 found stripped again 2026-10-21 (pre-fix runs) and reinstalled from main; seat2 and ~/.claude current
- **Last Verified:** 2026-10-19
- **Next Action:** agent_team repeats the fresh persona launch

## Step 10

- **Role:** Ticket worker
- **Owner / Assignment:** worker (wt/outcome)
- **Title:** 10. Outcome before close (Jordi via agent_team, 2026-10-20): every closed spine (done, abandoned, superseded) has `## Outcome` (verdict, one sentence, Done means -> evidence links, risk, closed date + agent); gate blocks a staged done spine without it; `spines.py --json` `outcome`; close rule says write Outcome, then close; parent rollup cites the sentence; [contract](console-contract.md#outcome)
- **Status:** done
- **Depends On:** none (independent of steps 1-3)
- **PR/Branch:** wt/outcome
- **Base:** main (branch removed)
- **Latest Evidence:** released 2026.10.20.2 (21adcba); test_outcome OK; `outcome` in --json; 2026-10-20; full suite 532 OK (1 skip) on 21adcba; release + JSON sent to agent_team
- **Last Verified:** 2026-10-21
- **Next Action:** none; agent_team backfills Outcome on m3-reddit-search, m4-browser-auth-sync

## Step 11

- **Role:** Ticket worker
- **Owner / Assignment:** worker (wt/outcome, same release as step 10)
- **Title:** 11. Current State for the console (Jordi via agent_team, 2026-10-20): `spines.py --json` `current_state` per node; doctrine: the manager updates Current State at the end of every working session or wake, not only at milestones, so the console's stale flag (Current State older than the last run) means something; [contract](console-contract.md#latest-state)
- **Status:** done
- **Depends On:** none
- **PR/Branch:** wt/outcome
- **Base:** main (branch removed)
- **Latest Evidence:** released 2026.10.20.2 (21adcba); `current_state` in --json; 2026-10-20; full suite 532 OK (1 skip) on 21adcba; release + JSON sent to agent_team
- **Last Verified:** 2026-10-21
- **Next Action:** none

## Step 12

- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5)
- **Title:** 12. Human asks (agent_team M2-SKILL, Jordi 2026-10-21): structured `## Waiting on` ask lines, answer write-back, `waiting_on` in --json, advisory checks; [contract](human-asks.md)
- **Status:** done
- **Depends On:** none
- **PR/Branch:** wt/human-asks
- **Base:** main
- **Latest Evidence:** released 2026.10.21.1 (merge 5672974); full isolated suite 554 OK; EPIC-4 waiting_on shows the open ask
- **Last Verified:** 2026-10-21
- **Next Action:** agent_team M2-13 reads `waiting_on`

## Step 13

- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5)
- **Title:** 13. sync_schedule.py takes its path from `__file__`: the background-sync cron entry can still point into a worktree; route it through install_guard
- **Status:** done
- **Depends On:** none
- **PR/Branch:** none
- **Base:** main
- **Latest Evidence:** released 2026.10.21.3 (merge 91011ec); isolated suite OK; real cron names the main checkout
- **Last Verified:** 2026-10-21
- **Next Action:** none

## Step 14

- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5)
- **Title:** 14. Learnings in force = the bound epic's plus every ancestor's up to the root (scope is the subtree); a persona on a leaf listed "none" and missed root L-1/L-2; one wording fix in global-block rule 1/2
- **Status:** done
- **Depends On:** none
- **PR/Branch:** none
- **Base:** main
- **Latest Evidence:** released 2026.10.21.4 (merge b1033ff); isolated suite 566 OK
- **Last Verified:** 2026-10-21
- **Next Action:** none

## Step 15

- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5)
- **Title:** 15. `current_state` omits Owner (and Approved work), yet the human-asks contract routes answers via `current_state.owner`; add both labels
- **Status:** done
- **Depends On:** none
- **PR/Branch:** merged
- **Base:** main
- **Latest Evidence:** released 2026.10.21.5; isolated suite 566 OK; EPIC-4 current_state.owner names this thread
- **Last Verified:** 2026-10-21
- **Next Action:** none

## Step 16

- **Role:** Ticket worker
- **Owner / Assignment:** worker seat2 (Sonnet 5.5)
- **Title:** 16. Workers bind "Learnings in force: none" even on 2026.10.21.4: a worker brief names no bound epic, so it never walks the parent chain; the dispatch brief template should name the epic (and its learnings chain)
- **Status:** done
- **Depends On:** none
- **PR/Branch:** merged
- **Base:** main
- **Latest Evidence:** released 2026.10.21.6; isolated suite OK; the step 16 worker itself bound with L-1..L-14 from EPIC-0
- **Last Verified:** 2026-10-21
- **Next Action:** none

## Step 17

- **Role:** Ticket worker
- **Owner / Assignment:** worker (Sonnet 5.5)
- **Title:** 17. Human asks v2 (agent_team M2-SKILL2, Jordi 2026-10-21): ask codes, `do` + steps, unblocks/effort, gate is not an ask, manager synthesis rule, answer by code; [contract v2](human-asks.md)
- **Status:** done
- **Depends On:** none
- **PR/Branch:** merged
- **Base:** main
- **Latest Evidence:** released 2026.10.21.7 (merge 2788fcf); full isolated suite OK; EPIC-4-A1 parses with code, unblocks, effort
- **Last Verified:** 2026-10-21
- **Next Action:** poly-maker E4 owner restates its gates as v2 asks

## Step 18

Pre-commit tests run from a linked worktree (for example `../epicspine-skill-wt-<task>`) exercise the hook the main checkout installed, so they test main's `pre_commit.py`, not the branch's. The step 3 worker found it on 2026-10-22 and ran its suite from a plain clone instead. Fix: the tests (or `install_guard`) resolve the hook script from the checkout under test. Back to [EPIC-4](../EPIC-4-DOCTRINE-2.md).

## Step 19

E4-5 cold check on EPIC-4, 2026-10-22, console run run_1d057709 (Sonnet 5.5, seat1). The brief was only `Bound epic: <path>` plus "read-only: change no files, commit nothing, dispatch no one, ask nothing".

Passed: no questions asked; it found the state, Done means, open ask EPIC-4-A2 and the linked pages; its checks (spines --json, --trackable, pages exist) agree with Current State.

Missed:
- it did not state the goal in its own words or its next action. It treated the brief as "verify the epic" (the read-only line may have pushed it there).
- it bound "Learnings in force: none read", without walking `Parent spine:` up to EPIC-0 (global-block rule 2).
- it reported `validate_spine.py --strict` failing with 32 ES-S-TICKET errors (Issue `draft` on non-draft rows). The doctrine says the ledger row is the ticket and `--strict` stays advisory, so this is expected; worth a one-line note in the doctrine or relaxing ES-S-TICKET for compact epics.

Fix (proposal): the bind reply of a worker whose brief is only `Bound epic:` states four lines from the spine (Goal, Done means left, Next action, where context lives) before acting, and walks the parent chain for learnings. Then re-run E4-5 without the read-only line, in a throwaway clone. Back to [EPIC-4](../EPIC-4-DOCTRINE-2.md).
