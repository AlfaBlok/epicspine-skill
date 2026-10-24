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
Last attempted: 2026-10-23 ticket-34 (e39fc79, skill 2026.10.23.1): ask lines agents write are all read (`superseded`, done notes, `Waiting on:` codes as `waits_on` refs), advisories name the canonical form
Result: EPIC-3 open items: E3-3 six rootless repos and E3-5, both gated on EPIC-3-A1
Evidence: e39fc79 (633 tests green; live `spines.py --json`: infra-vps EPIC-10-A8 superseded, EPIC-2-A9 done, Waiting-on refs); EPIC-3 011ab13
Waiting on: Jordi: EPIC-3-A1 (root spines for the six rootless repos; asked in EPIC-3)
Approved work: EPIC-3 Epic log and EPIC-4 Doctrine 2 (their ledgers hold the tickets)
Next action: EPIC-3 closes E3-2/E3-3/E3-5 (ETA 1-2 days, E3-3 rootless repos gated on EPIC-3-A1); EPIC-0 free for E3-5's learning; then close this root's DOD
Source revision: main
Verified at: 2026-10-23

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
- L-15..L-17 superseded: now skill doctrine (references/spine-model.md, global-block)

**Scoped index**: none yet.

## Definition Of Done

- [ ] DOD-1 A cold agent binds in three hops (AGENTS.md → this root spine → the branch matching its task), reading ≲ 100 lines before acting.
- [ ] DOD-2 The lean SKILL.md kernel and its Default Behaviors card are landed and installed copies re-synced.
- [ ] DOD-3 Strict graph validation and `python3 -B -m unittest discover -s tests` are green on main.

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | worker C (default profile) | Shortlist-by-default: JSON + generated sortable/filterable HTML as the default deliverable when a shortlist is key (port from abnb_agent SHORTLIST_STANDARD, check idea_scraper) | draft | none (SKILL.md/MANIFEST merge serialized after B) | wt/shortlist-default | 5fffe5a | dispatched | 2026-10-09 | verify diff + tests + served demo URL, ff-merge after B |
| draft | Ticket worker | worker G (Sonnet 5.5 subagent) | Always-on bind on every major harness: neutral global block + `install-global` + repo pointers + first-message route [detail](root/steps.md#ticket-11) | draft | none | wt/always-on-all-harnesses | a272d1f | integrated (ff-only, 5088c2f); 160 tests + block + validate + manifest green; install-global run here; cold "hi" pass on Claude Code, Codex, OpenCode; Gemini untested (no API key); worktree removed | 2026-10-10 | Gemini cold start |
| draft | Ticket worker | worker (Sonnet 5.5 subagent) | Enforce the served-URL rule on output: Stop hook `url_gate.py` + install-global wiring + rule line in both always-on blocks + handoff url/port/pid | draft | none | wt/url-gate | main | integrated (ff-only, 2346d2d); 193 tests + strict validate + block check + manifest green; e2e block/allow proof; worktree removed | 2026-10-11 | install-global on user OK |
| draft | Ticket worker | worker (Opus 5.5, T3 thread) | Enforce manager-never-implements and push-on-close with hooks: PreToolUse `manager_guard.py` (allowlist-first Bash/Edit policy, subagents via `agent_id`) + Stop `push_gate.py` | draft | none | PR #28 (feat/manager-guards) | 6ccb101 | PARKED 2026-10-13 by user: draft, not merged, not installed; 228 tests + CI green and e2e proven, but judged too complex/narrow/unpredictable. Do not merge, install, or build on it | 2026-10-13 | user revisits |
| draft | Ticket worker | worker (Sonnet 5.5, seat1 via seat pool) | Artifact host for remote readers: env `EPICSPINE_ARTIFACT_HOST` + `scripts/artifact_host.py`, url_gate host-aware, `install-global --artifact-host`, blocks + artifacts.md | draft | none | wt/artifact-host (removed) | 31aaf28 | integrated ff (6c5498c); 215 tests + validate + block + manifest green; round 2 rebased over be4c1d1 (round 1 would have reverted it); flag set on vps1 (3 seats + systemd drop-in) | 2026-10-14 | t3code restart picks up drop-in for non-Claude harnesses |
| draft | Ticket worker | worker (Sonnet 5.5, seat1 via seat pool) | Live shared rules: global block is the single source (hook-injected), thin repo block, pointer-only global files, self-migrating old repo blocks, supersede clause | draft | none | wt/live-rules (removed) | 1856f92 | integrated ff (c97e1ff) after r2 (hermetic tests; old repo block cannot outrank live rules) | 2026-10-14 | repos self-migrate on next session (agent_team, house_decision, sismic, zenod) |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Session autosync: SessionStart syncs skill, dispatch profile and repo; self-installs AGENTS.md block / Learnings; skill 2026.10.16.4 [detail](root/steps.md#ticket-22) | draft | none | feat/session-autosync | see branch | tests green (328), manifest regenerated, dry-run install on 3 real repo copies clean; Mac needs one-time bootstrap line | 2026-10-16 | delivery manager integrates; user runs the Mac line once |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Sync every step: Stop-hook push after every turn (Claude + Codex), AGENTS.md block in every repo with an origin; skill 2026.10.16.5 [detail](root/steps.md#ticket-23) | draft | none | feat/sync-every-step | see branch | tests green (352), real-codex test green (EPICSPINE_TEST_CODEX=1), Codex SessionStart+Stop verified against a mock model, manifest regenerated | 2026-10-16 | delivery manager integrates, then re-runs install-global on every config dir (VPS and Mac) |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Re-hook after update: SessionStart re-runs install-global so a self-updated machine registers new hooks; skill 2026.10.16.6 [detail](root/steps.md#ticket-24) | draft | none | fix/rehook-after-update | see branch | tests green (364), manifest regenerated | 2026-10-16 | draft |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Stale repo rules: a reversing learning sweeps the repo for instructions saying the old thing; vendored skill copies flagged; skill 2026.10.16.8 [detail](root/steps.md#ticket-26) | draft | none | feat/stale-repo-rules | see branch | tests green (373), manifest regenerated | 2026-10-16 | delivery manager integrates |
| draft | Ticket worker | worker (Opus 5.5, native) | Background sync: machine-wide cron/launchd job syncs every repo, writes `~/.agents/epicspine-sync-status.json`; skill 2026.10.16.9 [detail](root/steps.md#ticket-27) | draft | none | feat/background-sync | ad29302 | 421 tests green, manifest regenerated, real crontab untouched by tests | 2026-10-16 | merge per Integration policy; run install-global on the VPS and the Mac |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Fetch guard (infra-vps VH-T20): fetch timeouts kill git's process group, clean own tmp packs, back off after 2 strikes; skill 2026.10.20.1 [detail](root/steps.md#ticket-32) | draft | none | wt/fetch-timeout-tmp-pack | f63cf51 | new tests green; full suite differs from the pre-change baseline only by them (20 env failures pre-exist in this worktree); manifest regenerated | 2026-10-20 | manager merges |
| draft | Ticket worker | worker (Sonnet 5.5, native) | EPIC-4 steps 10+11: `## Outcome` before close and `current_state` in `--json`; `tests/test_outcome.py`; skill 2026.10.20.2 [detail](root/steps.md#ticket-33) | draft | none | wt/outcome | see branch | new tests green; manifest regenerated | 2026-10-20 | manager merges |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent) | ticket-34 Ask states & refs (agent_team L-12 duplicate cards): `superseded` state, done notes, `Waiting on:` codes as `waits_on[]` refs, advisories (D19 pt 4) | done | none | wt/ask-states-refs (removed) | 6be164a | merged e39fc79, 2026.10.23.1; 633 tests green; live JSON verified | 2026-10-23 | agent_team console codes against human-asks.md v4 |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent from agent_team EPIC-8 E8-S1) | ticket-35 Standing approvals: `[grant …]` lines, revoke/expiry, inheritance, `grants[]` in `--json`, advisories ([doctrine](doctrine/standing-approvals.md) v1) | done | none | wt/standing-approvals | 5bfaf22 | skill 2026.10.24.1; 643 tests green (10 new, tests/test_grants.py); live JSON on whatgpt_v3: EPIC-0 own E0-G1..G10, EPIC-1 inherits all 10 | 2026-10-24 | manager merges + releases; agent_team E8-S3 console Approvals codes against console-contract.md |
| draft | Ticket worker | worker (Opus 5.5, T3 sub-agent from agent_team EPIC-8 E8-S4) | ticket-36 Ask writing (agent_team L-13/L-14): blocking step only, decision first, one per ask; 3 advisories ([doctrine](doctrine/human-asks.md) v5) | done | none | wt/ask-writing | 2704724 | skill 2026.10.24.2; 649 tests green (6 new, tests/test_human_asks.py WritingTests) | 2026-10-24 | manager merges + releases |

Done tickets (20 rows, Next Action done/none, moved verbatim): [done ledger](root/steps.md#done-ledger).

## Decisions

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

## EpicSpine Book Companion

Status: active
Book root: index.html
Book steward: /root delivery manager
Chapter map: index.html (part-grouped slide index)
Leaf roots: index.html (single-file deck; leaves are slides)
Canonical registry: none
Registry row identity: none
Generated registry view: none
Author scope: slides of index.html plus tests/test_book_drift.py
Root promotion authority: Book steward
Registry write authority: read-only
Archive location: git history
Validation command: `uv run --with pytest pytest -q tests/test_book_drift.py`

Binding rule: When `Status: active`, every agent bound to this spine is also a Book author. For material research, comparison, recommendation, reusable explanation, or substantial user-facing synthesis, update or add a slide in index.html without a separate request.

Navigation rule: Every slide is reachable from the part-grouped index and links back to the Book root; the root promotes only current, foundational, or decision-significant slides.

Registry rule: No canonical registry; the Book keeps no live structured collection.

Landing exceptions: No slide for quick answers, transient status, raw logs, ticket debugging, or work with no durable user-facing knowledge.

## Spine Map

| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |
|---|---|---|---|---|---|---|---|---|
| epicspine-audit-remediation | child | [EPIC-2 Audit remediation](EPIC-2-AUDIT-REMEDIATION.md) | Audit remediation delivery | done | none | PR #16 | 2026-10-09 | Reference only; reopen if scope resumes |
| epicspine-coordination-simplification | child | [EPIC-1 Coordination simplification](EPIC-1-COORDINATION-SIMPLIFICATION.md) | Compact state and trustworthy rollups | done | none | PR #22 | 2026-10-09 | Reference only; reopen if scope resumes |
| epicspine-epic-log | child | [EPIC-3 Epic log](EPIC-3-EPIC-LOG.md) | Every goal is a coded EPIC in one tree per repo, kept true by agents | active | none | wt/epic-log r2 | 2026-10-19 | verify r2, merge, migrate poly-maker |
| epicspine-doctrine-2 | child | [EPIC-4 Doctrine 2 semantic goal tree](EPIC-4-DOCTRINE-2.md) | Contributes the human layer: every epic now says what it achieves and why, how it serves its parent and what each child adds, and the agent_team console shows it (Outcome: accomplished) | done | none | Outcome 2026-10-22; skill 2026.10.22.5 | 2026-10-22 | Reference only; reopen if scope resumes |
