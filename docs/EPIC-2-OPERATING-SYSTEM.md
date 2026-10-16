# EPIC: EpicSpine operating system

Spine profile: compact
Ticket backend: github
Spine dialect: v1
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-2-OPERATING-SYSTEM.md
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
Last attempted: 2026-10-16 session autosync (skill 2026.10.16.4, branch feat/session-autosync): the SessionStart hook now self-syncs (`session_sync.py`/`repo_sync.py`: skill ff/upgrade throttled 10 min, canonical `assets/epicspine-profile.md` -> `~/.agents/epicspine-profile.md` unless `.local.md`, current repo ff-pull/push per Integration policy, missing AGENTS.md block + Operating Learnings installed uncommitted); learnings are saved immediately with `Saved learning L-n … (say 'undo')`; `url_gate` only fires for HTML touched this turn. Cause of the drift: the hook only printed the block, `heal_repo` needed an existing block/Root spine, and upgrade was prose agents skipped. Before that: 2026-10-16 automatic trackable contract (skill 2026.10.16.3, cfa0526/8e51d2c/9f3c897): `validate_spine.py --trackable [--json]` (Status vocabulary, ID'd DoD/acceptance checkboxes, ledger Status; local: ticket-file Status) and `--fix` (`spine_fix.py`: criteria to `- [ ] <ID> text`, alias headings, status synonyms, header Status moved into Current State); pre-commit hook auto-fixes + re-stages, blocks only on guesses, `--strict` advisory; SessionStart installs the hook in EpicSpine repos. vps1 survey: 5/68 spines trackable before, 55 after auto-fix; 13 need a human (unmappable Status, mostly zenod/idea_scraper). Before that: 2026-10-16 machine-profile gap (skill 2026.10.16.2, 40cd545): SessionStart hook warns when `~/.agents/epicspine-profile.md` is missing (ask the user once, save with `profile --set`; never let workers silently inherit the manager's model); `install-global` prints a notice and takes `--profile TEXT`. Cause: vps1 had no machine profile, so workers inherited Opus; profile now written on vps1; sismic dispatch line → default (sismic 568f35f). Before that: 2026-10-16 machine-read contract (skill 2026.10.16.1, 760f0f8): `references/spine-model.md` states what dashboards read (DoD checkboxes, `Status:`/`Waiting on:`, Issue Ledger Issue/Title/Owner/Status with draft/ready/active/blocked/done/deferred; other tables not read); templates point to it; validator warns on a DoD without checkboxes (a github ledger missing Status already errors; local ledgers forbid Status by design). Before that: 2026-10-14 close-out (skill 2026.10.14.6): url_gate ignores quoted rule text; SessionStart hook heals a stale pasted CLAUDE.md copy into the pointer (no per-machine reinstall, Mac included) (77f4377); `install` touches only existing mirrors, `--mirrors` creates them (066dc43). Repos migrated to thin repo-1: agent_team d15b53d, house_decision a678023, sismic b7433df, zenod PR #1405; spine nits agent_team f4b31ed, sismic d45c610. Before that: 2026-10-14 live rules + headless auto-detect (skill 2026.10.14.4): shared rules live only in the skill (hook injects global-block.md each session; CLAUDE.md/Codex get a pointer; repo AGENTS.md block is thin `repo-1`, old copies superseded and self-migrated via the Migrate line, custom rule 3/4 lines carried over) (c97e1ff); artifact links go on Tailscale automatically on headless hosts, `EPICSPINE_ARTIFACT_HOST` is only an override (`local` opts out) (4f4fe25). vps1: install-global re-run (pointers, manual flag removed, systemd artifact-host.conf deleted). Before that: 2026-10-14 artifact host (skill 2026.10.14.2, 6c5498c): env `EPICSPINE_ARTIFACT_HOST` (`tailscale` = MagicDNS name + tailnet-IP bind; never 0.0.0.0/public) so HTML links open on the user's Mac/phone; url_gate accepts that host and blocks localhost-only replies when set; `install-global --artifact-host`. Set on vps1: settings.json env in ~/.claude, ~/.claude_seat1, ~/.claude_seat2 + systemd drop-in t3code.service.d/artifact-host.conf (applies on t3code restart). Before that: 2026-10-14 dispatch-suffix fix (skill 2026.10.14.1): the block line now forces the env check + `status` on every first turn, greetings included, and the name verbatim from `status.name`; vps1 saw 3 of 6 threads skip the suffix and invent "t3-seat-pool". Before that: 2026-10-13 machine dispatcher (`EPICSPINE_DISPATCHER` contract, `install-global --config-dir` + per-dir skill link, T3 seat-pool adapter in examples/) merged as PR #30, skill 2026.10.13.2; guard allowance PR #29 parked with #28. Before that: manager-guard + push-on-close hooks built as PR #28, then PARKED by user (draft, not merged; do not merge or build on it). Before that: 2026-10-11 Stop hook `url_gate.py` (blocks final replies that hand over HTML/visual files as paths instead of verified 127.0.0.1 URLs) integrated on main; install-global wiring included.
Result: 328 tests green (session autosync: skill/profile/repo sync + install + url_gate + learnings docs), manifest regenerated; dry-run install on copies of abnb-agent, tax-assist-research, testaments adds no validator diagnostics. Prior: 282 tests green, strict + graph validate, --trackable docs, block check, clean-tree manifest. Prior: 244 tests green, strict + graph validate, block check, clean-tree manifest; live: hook warns with empty HOME, silent with profile present. Prior: 242 tests green, strict + graph validate, block check, clean-tree manifest. Prior: 240 tests green under 3 env variants, strict validate, block check, manifest, CI. Prior: 227 tests green under 4 env variants (unset, tailscale, headless, DISPLAY), strict validate, block check, manifest; live clean-env proof: tailnet URL 200, gate allow/block, DISPLAY gives 127.0.0.1. Prior: 215 tests, strict validate, block check, manifest green on main @ 6c5498c; live: tailnet URL 200, loopback not exposed, gate allow/block proven. Prior: 200 tests, strict validate, block check, manifest green (2026.10.14.1); prior: CI green on main @ adbc1ce. Prior: 193 tests, strict validate, block check, manifest green on main; hook not yet installed on this machine. Prior: Book companion active (62a8852); profile show/set landed (04c28e0).
Evidence: [PR #30](https://github.com/AlfaBlok/epicspine-skill/pull/30), main @ adbc1ce
Waiting on: user on house_decision-m1d/m1e/m1f worktrees (uncommitted research; stale DeepSeek dispatch line): keep or discard
Approved work: none open
Next action: none open for this thread. Parked: PR #28 (Decisions 2026-10-13), Gemini cold start. Known: zenod vendors a manual skill copy (2026.10.09) by its own policy; zenod spine has 23 pre-existing strict-validate errors (zenod cleanup, not started).
Source revision: feat/session-autosync
Verified at: 2026-10-16
Last sweep: 2026-10-09, main clean
EpicSpine skill: 2026.10.10.1 @ 97b7535 (tree 59cc88f), checked 2026-10-10; hub upgraded; status via harness symlinks works

## Mission

Make EpicSpine the lean, automatic-default common ground for agent-assisted work and the living memory of a repository. A cold agent should bind fast, read little, and act correctly.

## Non-Goals

Not a product or runtime; not a general issue tracker; do not restate the skill's behaviors here (see its Default Behaviors card). EPIC-0 and EPIC-1 keep their own content and history.

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

**Scoped index**: none yet.

## Definition Of Done

- [ ] DOD-1 A cold agent binds in three hops (AGENTS.md → this root spine → the branch matching its task), reading ≲ 100 lines before acting.
- [ ] DOD-2 The lean SKILL.md kernel and its Default Behaviors card are landed and installed copies re-synced.
- [ ] DOD-3 Strict graph validation and `python3 -B -m unittest discover -s tests` are green on main.

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | /root delivery manager | Always-on AGENTS.md block + installer + CI check | draft | none | wt/agents-block | 1993233 | integrated on 02d7a88; 115 tests + block + manifest green; worktree removed | 2026-10-09 | done |
| draft | Ticket worker | /root/kernel (thread 441c3c64) | Lean SKILL.md kernel + Default Behaviors card + CI line budgets | draft | none | wt/kernel | main | integrated on d547410; 120 tests + agents_block check + strict validate + manifest green | 2026-10-09 | done |
| draft | Ticket worker | /root delivery manager | Centralize installed skill: hub + harness symlinks + pin SOURCE | draft | none | n/a | main | ~/.agents/skills/epic-spine real copy; Claude/OpenCode/Codex symlink to it; skill_update status fresh | 2026-10-09 | done |
| draft | Ticket worker | /root delivery manager | Cold-start test: fresh agent per provider binds and dispatches | draft | none | n/a | main | passed on opencode_2/deepseek-v4.1-flash: bound as delivery manager, named the default profile, card present, no dead ends | 2026-10-09 | done |
| draft | Ticket worker | worker A (default profile) | Default-behavior contract tests + SMOKE.md baseline | draft | none | wt/behavior-tests | b620d50 | integrated on 3108192; 125 tests green; mutation check fails as intended; smoke baseline P1 pass, P2 pass, P3 provisional pass (dry run stopped at first read; tighten preamble) | 2026-10-09 | done |
| draft | Ticket worker | worker B (default profile) | Adopt L-9..L-11 doctrine + extend tests/smoke | draft | worker A | wt/adopt-l9-l11 | 3108192 | integrated on a868281 (rebased over 7d617c2); 136 tests, strict validate, block check, manifest green; smoke 4/4 after P2 test rewrite (a694ae2) | 2026-10-09 | done |
| draft | Ticket worker | worker C (default profile) | Shortlist-by-default: JSON + generated sortable/filterable HTML as the default deliverable when a shortlist is key (port from abnb_agent SHORTLIST_STANDARD, check idea_scraper) | draft | none (SKILL.md/MANIFEST merge serialized after B) | wt/shortlist-default | 5fffe5a | dispatched | 2026-10-09 | verify diff + tests + served demo URL, ff-merge after B |
| draft | Ticket worker | worker D (default profile) | Shortlist template: table-first compact layout (user feedback on demo page) | draft | worker C | wt/shortlist-table-first | a868281 | integrated (ff-only, 7781d8e); 137 tests + strict validate + agents_block + manifest green; screenshot reviewed; demo re-served 200; worktree removed; installed skill upgraded | 2026-10-09 | done |
| draft | Ticket worker | worker E (Sonnet 5.5 subagent) | Vanilla dispatch default: shipped skill drops the author's hardwired profile; default becomes a lower-cost harness-native subagent; ask once when unset and record the answer as the root spine `Dispatch profile:`; AGENTS.md block defers to it | draft | none | wt/dispatch-defaults | 940d9f8 | integrated (ff-only, c3d2dc3); 138 tests + strict validate + agents_block + manifest green; roles-and-dispatch budget 100->105; worktree removed | 2026-10-10 | done |
| draft | Ticket worker | worker F (Sonnet 5.5 subagent) | Make skill updates actually work: content-tree freshness (not head commit), resolve harness symlinks to the hub, cache the last result not 'fresh', 1-day window, PR per user | draft | none | PR #27 | 974021d | merged ff (97b7535); 145 tests + CI + agents_block + manifest green; hub bootstrapped via real path, then upgrade + status --force via ~/.claude symlink = fresh; docs-only commit stays fresh; worktree removed | 2026-10-10 | done |
| draft | Ticket worker | worker G (Sonnet 5.5 subagent) | Always-on bind on every major harness: harness-neutral global block + `install-global` (instruction files + session hooks on by default; unsupported reported), repo pointers (CLAUDE.md/GEMINI.md -> AGENTS.md), first-message route | draft | none | wt/always-on-all-harnesses | a272d1f | integrated (ff-only, 5088c2f); 160 tests + block + validate + manifest green; install-global run here; cold "hi" pass on Claude Code, Codex, OpenCode; Gemini untested (no API key); worktree removed | 2026-10-10 | Gemini cold start |
| draft | Ticket worker | worker (Sonnet 5.5 subagent) | Machine-wide dispatch profile: one user-level file `~/.agents/epicspine-profile.md` used in every repo; repo `Dispatch profile:` only overrides; ask once and save at machine level | draft | none | wt/machine-profile | 3c12fbe | integrated (ff-only, ac3c4d4); 160 tests + agents_block + manifest green; machine file written; worktree removed | 2026-10-10 | done |
| draft | Ticket worker | worker (Sonnet 5.5 subagent) | Enforce the served-URL rule on output: Stop hook `url_gate.py` + install-global wiring + rule line in both always-on blocks + handoff url/port/pid | draft | none | wt/url-gate | main | integrated (ff-only, 2346d2d); 193 tests + strict validate + block check + manifest green; e2e block/allow proof; worktree removed | 2026-10-11 | install-global on user OK |
| draft | Ticket worker | worker (Sonnet 5.5 subagent) | Profile command + cold-start test: `profile` show/set command for `~/.agents/epicspine-profile.md`; docs point to it; tests prove ask-once, save, reuse across repos | draft | none | wt/profile-command | fcddfe5 | integrated (ff-only, 04c28e0); 165 tests + agents_block + manifest green; `profile` verified live (machine, rc 0) and empty home (unset, rc 3); worktree removed | 2026-10-10 | done |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Machine dispatcher: env `EPICSPINE_DISPATCHER` (status/pick/done JSON, via t3_delegate_task) routes workers on any host; repo opt-out `Dispatch profile: local-only`; `install-global --config-dir` links the skill per Claude config dir | draft | none | PR #30 (merged); PR #29 guard allowance parked with #28 | adbc1ce | 200 tests + CI green; agent_team rollout done (4026755, 7dea50c), block 2026.10.13.2 live on vps1 | 2026-10-13 | done |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Dispatch suffix always: block line forces env check + `status` on every first turn (greetings included), suffix `· dispatch: <status.name> (<available>/<capacity> seats)` verbatim, rule 1 pointer; skill 2026.10.14.1 | draft | none | fix/dispatch-suffix-always | be4c1d1 | tests + strict validate + manifest green; vps1 reinstall done, bare-"hi" retest pass on seat1/seat2 | 2026-10-14 | done |
| draft | Ticket worker | worker (Opus 5.5, T3 thread) | Enforce manager-never-implements and push-on-close with hooks: PreToolUse `manager_guard.py` (allowlist-first Bash/Edit policy, subagents via `agent_id`) + Stop `push_gate.py` | draft | none | PR #28 (feat/manager-guards) | 6ccb101 | PARKED 2026-10-13 by user: draft, not merged, not installed; 228 tests + CI green and e2e proven, but judged too complex/narrow/unpredictable. Do not merge, install, or build on it | 2026-10-13 | user revisits |
| draft | Ticket worker | worker (Sonnet 5.5, seat1 via seat pool) | Artifact host for remote readers: env `EPICSPINE_ARTIFACT_HOST` + `scripts/artifact_host.py`, url_gate host-aware, `install-global --artifact-host`, blocks + artifacts.md | draft | none | wt/artifact-host (removed) | 31aaf28 | integrated ff (6c5498c); 215 tests + validate + block + manifest green; round 2 rebased over be4c1d1 (round 1 would have reverted it); flag set on vps1 (3 seats + systemd drop-in) | 2026-10-14 | t3code restart picks up drop-in for non-Claude harnesses |
| draft | Ticket worker | worker (Sonnet 5.5, seat1 via seat pool) | Live shared rules: global block is the single source (hook-injected), thin repo block, pointer-only global files, self-migrating old repo blocks, supersede clause | draft | none | wt/live-rules (removed) | 1856f92 | integrated ff (c97e1ff) after r2 (hermetic tests; old repo block cannot outrank live rules) | 2026-10-14 | repos self-migrate on next session (agent_team, house_decision, sismic, zenod) |
| draft | Ticket worker | worker (Sonnet 5.5, seat2 via seat pool) | Headless auto-detect: no display + Tailscale up gives tailnet links with no setup; env only overrides | draft | none | wt/auto-host (removed) | c97e1ff | integrated ff (4f4fe25) after r2 rebase; vps1 manual flag removed | 2026-10-14 | done |
| draft | Ticket worker | workers (Sonnet 5.5, seat pool) | Close-out: gate quote fix, self-healing global copy, install mirror scope, migrate 4 repo blocks + spine nits | draft | none | wt/selfheal, wt/install-scope (removed); zenod PRs #1405, #1406, #1407 (restored vendored-copy line) | dbe9d4f | integrated ff (77f4377, 066dc43); 240 tests x3 env green; 4 repos check rc 0 | 2026-10-14 | done |
| draft | Ticket worker | worker (Sonnet 5.5, native) | Session autosync: SessionStart syncs skill + canonical dispatch profile + current repo and self-installs the AGENTS.md block / Operating Learnings; learnings saved immediately; url_gate fires only for HTML touched this turn; skill 2026.10.16.4 | draft | none | feat/session-autosync | see branch | tests green (328), manifest regenerated, dry-run install on 3 real repo copies clean; Mac needs one-time bootstrap line | 2026-10-16 | delivery manager integrates; user runs the Mac line once |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-16 | accepted | Automatic trackable contract | Enforcement is `--trackable`, never `--strict` (advisory). The pre-commit hook fixes what is unambiguous and blocks only on guesses; it self-installs via SessionStart. Local-backend ledgers: ticket-file Status counts. DoD criteria are `- [ ] <ID> text` (agent_team proposal). | user decisions 2026-10-16 | Dashboards need more fields |
| 2026-10-09 | accepted | Two base roles | Every agent is a delivery manager or a worker; older identities are remits under them. | user decision 2026-10-09 | Role model changes |
| 2026-10-09 | accepted | Stay in main, manager merges | Workers use local wt/<task> worktrees; the manager merges verified work to main. | user decision 2026-10-09 | User asks for PR review |
| 2026-10-09 | accepted | Learnings tree | Root Always list plus a scoped index; depth is scope. | user decision 2026-10-09 | Learning model changes |
| 2026-10-09 | accepted | Sweep as a worker brief | Hygiene is a dispatched brief, not a third base role. | user decision 2026-10-09 | Sweep needs its own role |
| 2026-10-09 | accepted | Skill updates auto | `Skill updates: auto` is the default; upgrade between tasks. | user decision 2026-10-09 | User prefers manual |
| 2026-10-09 | accepted | EPIC-0 and EPIC-1 closed | Both prior epics are done children of this root; their content is preserved. | user decision 2026-10-09 | Delivery scope resumes |
| 2026-10-09 | accepted | Root wiring | This compact spine is the single root; EPIC-0 and EPIC-1 are its direct children. | user decision 2026-10-09 | Hierarchy needs re-scoping |
| 2026-10-09 | accepted | No unrequested model changes | Every subagent, reviewers included, uses the default profile unless the user asks; fresh context gives review independence. | user decision 2026-10-09 | User names another model |
| 2026-10-09 | accepted | Serialize MANIFEST-changing merges | One writer per spine and one MANIFEST merge at a time: agents-block landed first, kernel rebases second; the second merge regenerates MANIFEST. | thread collision a0380f46 vs 441c3c64 | Two branches touch MANIFEST |
| 2026-10-09 | accepted | Comparison adoption fork | Adopt L-9 (resolve decisions before dispatch), L-10 (ready frontier), L-11 (two-axis verification) in our own words from the Pocock/poteto comparison. Guarded by tags checkpoint/pre-adoption (b620d50) and checkpoint/post-adoption, plus contract tests and a dry-run smoke test. Revert = `git revert b620d50..HEAD`, then re-sync the installed skill; never reset public main. | user decision 2026-10-09; thread a0380f46 | Smoke or contract tests regress |
| 2026-10-09 | accepted | L-9 asks on missing details | L-9 stays as written: when an instruction leaves out a detail, the agent asks one clear question with a recommendation before dispatching. The P2 smoke prompt was a bad test (an unspecified typo), not a rule regression; P2 is rewritten as a fully specified edit and the ask-first behavior stays covered by P4. | user decision 2026-10-09 | Over-asking becomes a recurring complaint |
| 2026-10-10 | accepted | Shipped default vs repo profile | The public skill ships a vague vanilla default (lower-cost harness-native worker); a user's profile is stored per repo as the root spine `Dispatch profile:` and wins thereafter. This repo's profile: native subagent, Sonnet 5.5. Supersedes the 2026-10-09 hardwired DeepSeek default. | user decision 2026-10-10 | User changes profile |
| 2026-10-10 | accepted | Skill freshness by content | Freshness = git tree hash of `skill/epic-spine/` (pin `tree:`), not repo head; harness symlinks resolve to the real hub; only a symlink into a git checkout or a vendored pin is `linked`; cache returns the last result; default window 1 day. | user report 2026-10-10 (false stale; harness `linked`) | Freshness misreports again |
| 2026-10-10 | accepted | Always-on is harness-neutral | Installing EpicSpine must make every major agent bind on its first reply in any repo; no harness is the default. Delivery: a global block in each harness's user-level instruction file, per-adapter hooks where they exist, and repo pointers for harnesses that don't read AGENTS.md. Done only when a cold start in a blockless repo passes. | user decision 2026-10-10 | A major harness fails cold start |
| 2026-10-10 | accepted | Profile is machine-wide | The user sets the worker profile once per machine (`~/.agents/epicspine-profile.md`); every repo uses it; a repo's `Dispatch profile:` line only overrides. Unset everywhere: ask once, save at machine level. Supersedes per-repo ask-and-record. | user decision 2026-10-10 | User wants per-repo profiles |
| 2026-10-13 | accepted | Park manager guard via blocking hooks (PR #28) | Hard-blocking the manager with a heuristic PreToolUse shell/edit policy, plus a push-on-close Stop hook, is parked: the user doesn't trust it (complex, Claude Code + main checkout only, unpredictable false positives). Preferred direction: reinforce the rule by re-injecting a short manager reminder every turn and after compaction, not blocking. Open gaps if revisited: non-isolated subagents, non-Claude harnesses, `gh pr create` under pr-approval, git pre-commit layer, scheduled push-backlog sweep. | user decision 2026-10-13; PR #28 comment | User revisits enforcement |
| 2026-10-14 | accepted | Artifact host is machine env | Remote/headless hosts set `EPICSPINE_ARTIFACT_HOST` (`tailscale` default path, no root); links use the MagicDNS name, the server binds the tailnet IP only; unset keeps 127.0.0.1. `tailscale serve` HTTPS is an optional upgrade. | infra-vps request 2026-10-14 | User wants HTTPS or another network |
| 2026-10-14 | accepted | Shared rules live only in the skill | Improving EpicSpine = merge to main; every repo and seat gets it next session. Repos hold only repo values; an old repo copy never outranks the live block. Machine install once; artifact host auto-detected (supersedes the per-machine flag of the same day). | user intent 2026-10-14 | A harness without hooks misbehaves |

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
| epicspine-audit-remediation | child | [EPIC-0 Audit remediation](EPIC-0-AUDIT-REMEDIATION.md) | Audit remediation delivery | done | none | PR #16 | 2026-10-09 | Reference only; reopen if scope resumes |
| epicspine-coordination-simplification | child | [EPIC-1 Coordination simplification](EPIC-1-COORDINATION-SIMPLIFICATION.md) | Compact state and trustworthy rollups | done | none | PR #22 | 2026-10-09 | Reference only; reopen if scope resumes |
