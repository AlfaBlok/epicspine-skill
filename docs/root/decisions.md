# Decisions of the root spine: detail

Page of [EPIC-0](../EPIC-0-OPERATING-SYSTEM.md). The Decisions table there keeps one line per decision; the full Durable Summary of each row over 200 characters, as it stood in the table, is here. Decisions are numbered by row position in the table (rows that fit stay in the table only).

## D 2

- **Date:** 2026-10-16
- **Outcome:** accepted
- **Decision / Attempt:** Automatic trackable contract
- **Durable Summary:** Enforcement is `--trackable`, never `--strict` (advisory). The pre-commit hook fixes what is unambiguous and blocks only on guesses; it self-installs via SessionStart. Local-backend ledgers: ticket-file Status counts. DoD criteria are `- [ ] <ID> text` (agent_team proposal).
- **Evidence:** user decisions 2026-10-16
- **Revisit When:** Dashboards need more fields

## D 12

- **Date:** 2026-10-09
- **Outcome:** accepted
- **Decision / Attempt:** Comparison adoption fork
- **Durable Summary:** Adopt L-9 (resolve decisions before dispatch), L-10 (ready frontier), L-11 (two-axis verification) in our own words from the Pocock/poteto comparison. Guarded by tags checkpoint/pre-adoption (b620d50) and checkpoint/post-adoption, plus contract tests and a dry-run smoke test. Revert = `git revert b620d50..HEAD`, then re-sync the installed skill; never reset public main.
- **Evidence:** user decision 2026-10-09; thread a0380f46
- **Revisit When:** Smoke or contract tests regress

## D 13

- **Date:** 2026-10-09
- **Outcome:** accepted
- **Decision / Attempt:** L-9 asks on missing details
- **Durable Summary:** L-9 stays as written: when an instruction leaves out a detail, the agent asks one clear question with a recommendation before dispatching. The P2 smoke prompt was a bad test (an unspecified typo), not a rule regression; P2 is rewritten as a fully specified edit and the ask-first behavior stays covered by P4.
- **Evidence:** user decision 2026-10-09
- **Revisit When:** Over-asking becomes a recurring complaint

## D 14

- **Date:** 2026-10-10
- **Outcome:** accepted
- **Decision / Attempt:** Shipped default vs repo profile
- **Durable Summary:** The public skill ships a vague vanilla default (lower-cost harness-native worker); a user's profile is stored per repo as the root spine `Dispatch profile:` and wins thereafter. This repo's profile: native subagent, Sonnet 5.5. Supersedes the 2026-10-09 hardwired DeepSeek default.
- **Evidence:** user decision 2026-10-10
- **Revisit When:** User changes profile

## D 15

- **Date:** 2026-10-10
- **Outcome:** accepted
- **Decision / Attempt:** Skill freshness by content
- **Durable Summary:** Freshness = git tree hash of `skill/epic-spine/` (pin `tree:`), not repo head; harness symlinks resolve to the real hub; only a symlink into a git checkout or a vendored pin is `linked`; cache returns the last result; default window 1 day.
- **Evidence:** user report 2026-10-10 (false stale; harness `linked`)
- **Revisit When:** Freshness misreports again

## D 16

- **Date:** 2026-10-10
- **Outcome:** accepted
- **Decision / Attempt:** Always-on is harness-neutral
- **Durable Summary:** Installing EpicSpine must make every major agent bind on its first reply in any repo; no harness is the default. Delivery: a global block in each harness's user-level instruction file, per-adapter hooks where they exist, and repo pointers for harnesses that don't read AGENTS.md. Done only when a cold start in a blockless repo passes.
- **Evidence:** user decision 2026-10-10
- **Revisit When:** A major harness fails cold start

## D 17

- **Date:** 2026-10-10
- **Outcome:** accepted
- **Decision / Attempt:** Profile is machine-wide
- **Durable Summary:** The user sets the worker profile once per machine (`~/.agents/epicspine-profile.md`); every repo uses it; a repo's `Dispatch profile:` line only overrides. Unset everywhere: ask once, save at machine level. Supersedes per-repo ask-and-record.
- **Evidence:** user decision 2026-10-10
- **Revisit When:** User wants per-repo profiles

## D 18

- **Date:** 2026-10-13
- **Outcome:** accepted
- **Decision / Attempt:** Park manager guard via blocking hooks (PR #28)
- **Durable Summary:** Hard-blocking the manager with a heuristic PreToolUse shell/edit policy, plus a push-on-close Stop hook, is parked: the user doesn't trust it (complex, Claude Code + main checkout only, unpredictable false positives). Preferred direction: reinforce the rule by re-injecting a short manager reminder every turn and after compaction, not blocking. Open gaps if revisited: non-isolated subagents, non-Claude harnesses, `gh pr create` under pr-approval, git pre-commit layer, scheduled push-backlog sweep.
- **Evidence:** user decision 2026-10-13; PR #28 comment
- **Revisit When:** User revisits enforcement

## D 19

- **Date:** 2026-10-14
- **Outcome:** accepted
- **Decision / Attempt:** Artifact host is machine env
- **Durable Summary:** Remote/headless hosts set `EPICSPINE_ARTIFACT_HOST` (`tailscale` default path, no root); links use the MagicDNS name, the server binds the tailnet IP only; unset keeps 127.0.0.1. `tailscale serve` HTTPS is an optional upgrade.
- **Evidence:** infra-vps request 2026-10-14
- **Revisit When:** User wants HTTPS or another network

## D 20

- **Date:** 2026-10-14
- **Outcome:** accepted
- **Decision / Attempt:** Shared rules live only in the skill
- **Durable Summary:** Improving EpicSpine = merge to main; every repo and seat gets it next session. Repos hold only repo values; an old repo copy never outranks the live block. Machine install once; artifact host auto-detected (supersedes the per-machine flag of the same day).
- **Evidence:** user intent 2026-10-14
- **Revisit When:** A harness without hooks misbehaves

## D 21

- **Date:** 2026-10-19
- **Outcome:** accepted
- **Decision / Attempt:** Epic log = tree of goals
- **Durable Summary:** A goal is measurably accomplishable (checkbox DoD saying how it is measured) and states its purpose beyond the metric (Mission). Spines are nested markdowns, one tree per repo, hung from the root (purpose). Judgment, not a hard rule: progress within a spine is written in that spine (state, ledger, DoD lines); a new measurable objective worked over iterative pushes (a sprint or plan, each push unblocking the next) gets a new leaf markdown, linked from its parent. Child `Parent spine:` is the structural authority; parent Spine Map must agree (checked). Parent state rolls up from children. Words: spine = trunk, goal/epic = node, epic log = the tree; no file/header rename. "On latest" = installed AND docs conform.
- **Evidence:** user decision 2026-10-19 (handoff docs/handoffs/2026-10-19-spine-conformance.md)
- **Revisit When:** Repos need a cross-repo portfolio root

## Decisions table

Rows moved verbatim from the [EPIC-0](../EPIC-0-OPERATING-SYSTEM.md) Decisions table (add new rows at the top).

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-19 | accepted | Personas lost the doctrine | "Installed" also needs every config dir (seat1, ~/.claude) pointing at the canonical checkout with hooks; tests must never touch real config. Detail and fix: EPIC-4 step 9. | EPIC-4 845e6ff | step 9 merged |
| 2026-10-16 | accepted | Automatic trackable contract | Enforcement is `--trackable`, never `--strict`; the pre-commit hook fixes the unambiguous and blocks only on guesses; self-installs via SessionStart. [detail](root/decisions.md#d2) | user decisions 2026-10-16 | Dashboards need more fields |
| 2026-10-09 | accepted | Two base roles | Every agent is a delivery manager or a worker; older identities are remits under them. | user decision 2026-10-09 | Role model changes |
| 2026-10-09 | accepted | Stay in main, manager merges | Workers use local wt/<task> worktrees; the manager merges verified work to main. | user decision 2026-10-09 | User asks for PR review |
| 2026-10-09 | accepted | Learnings tree | Root Always list plus a scoped index; depth is scope. | user decision 2026-10-09 | Learning model changes |
| 2026-10-09 | accepted | Sweep as a worker brief | Hygiene is a dispatched brief, not a third base role. | user decision 2026-10-09 | Sweep needs its own role |
| 2026-10-09 | accepted | Skill updates auto | `Skill updates: auto` is the default; upgrade between tasks. | user decision 2026-10-09 | User prefers manual |
| 2026-10-09 | accepted | EPIC-2 and EPIC-1 closed | Both prior epics are done children of this root; their content is preserved. | user decision 2026-10-09 | Delivery scope resumes |
| 2026-10-09 | accepted | Root wiring | This compact spine is the single root; EPIC-2 and EPIC-1 are its direct children. | user decision 2026-10-09 | Hierarchy needs re-scoping |
| 2026-10-09 | accepted | No unrequested model changes | Every subagent, reviewers included, uses the default profile unless the user asks; fresh context gives review independence. | user decision 2026-10-09 | User names another model |
| 2026-10-09 | accepted | Serialize MANIFEST-changing merges | One writer per spine and one MANIFEST merge at a time: agents-block landed first, kernel rebases second; the second merge regenerates MANIFEST. | thread collision a0380f46 vs 441c3c64 | Two branches touch MANIFEST |
| 2026-10-09 | accepted | Comparison adoption fork | Adopt L-9, L-10 and L-11 in our own words from the Pocock/poteto comparison; tags checkpoint/pre-adoption (b620d50) and checkpoint/post-adoption guard it. [detail](root/decisions.md#d12) | user decision 2026-10-09; thread a0380f46 | Smoke or contract tests regress |
| 2026-10-09 | accepted | L-9 asks on missing details | L-9 stays as written: ask one clear question with a recommendation when a detail is missing; the P2 smoke prompt was the bad test, rewritten. [detail](root/decisions.md#d13) | user decision 2026-10-09 | Over-asking becomes a recurring complaint |
| 2026-10-10 | accepted | Shipped default vs repo profile | The public skill ships a vague vanilla default (lower-cost native worker); a repo's `Dispatch profile:` wins; this repo: native subagent, Sonnet 5.5. [detail](root/decisions.md#d14) | user decision 2026-10-10 | User changes profile |
| 2026-10-10 | accepted | Skill freshness by content | Freshness = git tree hash of `skill/epic-spine/`, not repo head; harness symlinks resolve to the hub; cache returns the last result; 1-day window. [detail](root/decisions.md#d15) | user report 2026-10-10 (false stale; harness `linked`) | Freshness misreports again |
| 2026-10-10 | accepted | Always-on is harness-neutral | Installing EpicSpine makes every major agent bind on its first reply in any repo: global block, per-adapter hooks, repo pointers; done on a cold-start pass. [detail](root/decisions.md#d16) | user decision 2026-10-10 | A major harness fails cold start |
| 2026-10-10 | accepted | Profile is machine-wide | The worker profile is set once per machine (`~/.agents/epicspine-profile.md`); a repo's `Dispatch profile:` only overrides; unset: ask once, save there. [detail](root/decisions.md#d17) | user decision 2026-10-10 | User wants per-repo profiles |
| 2026-10-13 | accepted | Park manager guard via blocking hooks (PR #28) | Hard-blocking the manager with PreToolUse/Stop hooks (PR #28) is parked as complex and unpredictable; preferred: re-inject a short manager reminder. [detail](root/decisions.md#d18) | user decision 2026-10-13; PR #28 comment | User revisits enforcement |
| 2026-10-14 | accepted | Artifact host is machine env | Remote/headless hosts set `EPICSPINE_ARTIFACT_HOST` (`tailscale` default); links use MagicDNS, the server binds the tailnet IP only; unset keeps 127.0.0.1. [detail](root/decisions.md#d19) | infra-vps request 2026-10-14 | User wants HTTPS or another network |
| 2026-10-14 | accepted | Shared rules live only in the skill | Improving EpicSpine = merge to main; repos hold only repo values; an old repo copy never outranks the live block; artifact host auto-detected. [detail](root/decisions.md#d20) | user intent 2026-10-14 | A harness without hooks misbehaves |
| 2026-10-19 | accepted | Epic log = tree of goals | A goal is measurably accomplishable and states its purpose; spines are nested markdowns, one tree per repo; child `Parent spine:` is authoritative. [detail](root/decisions.md#d21) | user decision 2026-10-19 (handoff docs/handoffs/2026-10-19-spine-conformance.md) | Repos need a cross-repo portfolio root |
