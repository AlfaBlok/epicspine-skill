# Changelog

## Unreleased — session autosync

- SessionStart now syncs instead of only printing the block (`scripts/session_sync.py`, `scripts/repo_sync.py`; one 10 s deadline, short per-call git timeouts, never raises, never forces; `EPICSPINE_SYNC=off` disables; the hook adds `EpicSpine sync:/setup:/attention:` lines to additionalContext). **Skill**, at most once per 10 minutes (stamp `~/.agents/epicspine-sync.stamp`): a source checkout (`<repo>/skill/epic-spine`) is fetched and fast-forwarded when clean and only behind; a pinned/unpinned installed copy runs `skill_update.py`'s verified upgrade when `ls-remote` shows a new commit (`cmd_upgrade` takes a `timeout`); vendored copies and repos with `Skill updates: off|manual` are skipped; reports `skill 2026.10.16.3 -> 2026.10.16.4`. **Repo**: fetch; clean + only behind -> ff-only; ahead on the integration branch -> push (ff-only, not under `Integration policy: pr-approval`); diverged or dirty-and-behind on the integration branch -> nothing changes, an `attention` line names the repo and why; detached, mid-merge/rebase, offline and no-origin are silent. **Repo setup**: a repo with a discoverable root spine (AGENTS.md block's `Root spine:`, else the one tracked epic/spine-named `.md` with a `## Current State` that is not a child) but no current AGENTS.md block gets `agents_block.py install`, and a root spine lacking `## Operating Learnings` gets an empty Always/Scoped-index section, left uncommitted with one line asking the agent to commit. Cause of the abnb-agent gap: `heal_repo` only installed the pre-commit gate, and only when a block or `Root spine:` line already existed; `install` also demanded `--root-spine` when no block existed. Repos with no root spine stay untouched (the block's offer-once rule applies).
- One canonical dispatch profile: `assets/epicspine-profile.md`; the hook (and `install-global`) rewrites `~/.agents/epicspine-profile.md` from it unless `~/.agents/epicspine-profile.local.md` exists. `agents_block.py profile --set` now writes that local override; precedence repo `Dispatch profile:` > local > synced machine file. The missing-profile warning stays only while neither exists.
- Learnings are saved, not proposed: on a repeated correction or an always/never/I prefer statement the agent writes the line at once into the right spine's Operating Learnings and ends the reply with `Saved learning L-<n>: <rule> (say 'undo' to remove)`; propose-and-wait and throttling removed (`references/learnings.md`, global block rule 7, SKILL.md).
- `url_gate.py`: a path mention only blocks when the file was created/modified this turn (transcript Write/Edit targets, or mtime at/after the last user prompt) or its line says open/view/deliverable; `file://` links always count; no transcript/timestamps keeps the old behavior. Naming `assets/shortlist.template.html` as a source no longer blocks. Skill 2026.10.16.4.

## Unreleased — trackable gate

- `validate_spine.py --trackable [--json]` checks only the machine-read contract: Current State `Status:` (tickets: `Status:`) in draft/ready/active/blocked/done/deferred; under the canonical `## Definition Of Done` (tickets: `## Acceptance`/`## Acceptance Criteria`) every criterion is `- [ ] <ID> <text>` / `- [x] <ID> ...` (ID `[A-Z][A-Z0-9]*-\d+`, unique per file; indented lines continue an item; prose, tier labels, HTML comments and fences are not criteria) with at least one; a ledger Status column (local backend: every referenced ticket file has a valid Status instead). Independent of `--strict`; exit 0 iff all pass; JSON is a per-file list of `path`/`trackable`/`missing`/`warnings`.
- `validate_spine.py --fix <paths>` (new `scripts/spine_fix.py`) repairs in place, idempotently, without changing criterion text: numbered/bullet/ID-less criteria become `- [ ] <ID> <text>` (existing IDs kept; new ones continue the file's most common prefix, else `DOD`/`AC`); spine alias headings (`## Exit Test...`, `## Acceptance`) become `## Definition Of Done`; Status synonyms (in progress/wip/doing/review/testing→active, todo/planned/open/backlog→ready, closed/complete/delivered/superseded/shipped/merged→done, on hold/paused/parked→deferred, proposed→draft; defined once in `SYNONYMS`; ambiguous leading words like current/generic/prior/guest are never mapped) are mapped in Current State, tickets and Issue Ledger cells; a lone preamble `Status:` (also `**Status:**`) in a spine with none in Current State is moved (not copied) into Current State as its first line and then mapped, and the validator accepts a Status in either place for the full-profile `Status` field, so strict results do not change. A missing Status line/column or empty Definition Of Done is never invented and still blocks.
- `agents_block.py install` writes a pre-commit hook (honors `core.hooksPath`, never replaces a foreign hook, `uninstall` removes only ours; `check` notes its absence without failing) running `scripts/pre_commit.py`: each staged spine/ticket `.md` that is not trackable is auto-fixed and re-staged when it has no unstaged changes (one `epicspine: fixed <file>: ...` line each), blocked with the exact `--fix` command when it has, and blocked with a precise reason only when a guess would be needed (an unmappable Status shows its value and the allowed words: `Current State Status 'SHIP candidate — ...': start it with one of draft|ready|active|blocked|done|deferred`); `--strict` is advisory. The SessionStart hook installs the gate silently in any git repo with an EpicSpine AGENTS.md block or `Root spine:` file, so no per-repo command is needed. Templates and examples use `- [ ] <ID> ...`. Skill 2026.10.16.3.

## Unreleased — machine profile gap

- The SessionStart hook (`print-hook`) appends a warning line when `~/.agents/epicspine-profile.md` is missing (ask the user once, save with `profile --set`; workers must not silently inherit the manager's model); no warning when it exists. `install-global` prints a notice when it is missing, and `--profile TEXT` writes it via the `profile --set` path; no default model is ever written. Skill 2026.10.16.2.

## Unreleased — machine-read contract

- Spine docs/templates state the machine-read contract (`spine-model.md`): dashboards read only DoD checkboxes, Current State `Status:`/`Waiting on:`, and the Issue Ledger's Issue/Title/Owner/Status (draft/ready/active/blocked/done/deferred). `validate_spine.py` warns (advisory) when Definition Of Done has no checkbox line. Skill 2026.10.16.1.

## Unreleased — install scope

- `agents_block.py install --repo` now always writes `AGENTS.md` but updates a harness mirror (`CLAUDE.md`, `GEMINI.md`, `.cursor/rules/epicspine.mdc`, `.github/copilot-instructions.md`) only if it already exists; new `--mirrors` creates the missing ones. Self-migrating an old repo (the global block's Migrate line) no longer litters it with untracked files. `check` only looks at mirrors that exist; `uninstall` is unchanged. Skill 2026.10.14.6.

## Unreleased — gate quoting + self-heal

- `url_gate.py` no longer blocks a reply that only quotes the rule wording: a bare `file://` and URLs carrying a `<placeholder>` (`http://<host>:<port>/<file>`) are not visual mentions or URLs to curl; real file URLs, slash paths, "open x" and unreachable URLs still block.
- The SessionStart hook (`print-hook`) now also heals, best-effort and silently, a stale EpicSpine block in the user-level `CLAUDE.md` (`CLAUDE_CONFIG_DIR`, else `~/.claude`): an old pasted full copy becomes the pointer, in place and atomically (`upsert` now writes atomically), nothing else touched; a current or absent block is left alone. Machines installed earlier need no manual reinstall. Skill 2026.10.14.5.

## Unreleased — artifact host auto-detect

- `artifact_host.resolve()` now detects a headless machine (not macOS/Windows, no `DISPLAY`/`WAYLAND_DISPLAY`/x11-wayland `XDG_SESSION_TYPE`) with a working Tailscale and serves on the tailnet by default, with zero per-machine setup; desktops and headless hosts without Tailscale stay on `127.0.0.1`, silently. `EPICSPINE_ARTIFACT_HOST` is now only an override: `local` (or `127.0.0.1`) forces loopback, `tailscale` and hostnames behave as before (still warn on failure). Subprocess timeout 3s. Always-on HTML line, `artifacts.md`, README and `--artifact-host` help reworded. Skill 2026.10.14.4.

## Unreleased — live rules

- Shared rules now live only in the skill: `assets/global-block.md` (injected live by the session hook) carries bind, dispatch, integrate, record, HTML/artifact-host, machine-dispatcher and a migrate line. `assets/agents-block.md` is a thin repo block (root spine, pointer, repo-values override, precedence) with a stable id (`repo-1`) instead of the skill version, so releases never stale it. `install-global` writes a short pointer to the live global block (absolute skill path) instead of a pasted copy. `agents_block.py install --repo .` migrates an old full block (root spine kept, `--root-spine` optional; non-stock worker/integrate lines carried over below the block) and `check` reports old blocks as stale. Skill 2026.10.14.3.

## Unreleased — artifact host

- Env `EPICSPINE_ARTIFACT_HOST` (`tailscale` or a hostname) makes artifacts serve on the tailnet/private address and be reported as `http://<host>:<port>/<file>`, for headless hosts read from another device; optional `EPICSPINE_ARTIFACT_BIND`; never binds `0.0.0.0` or a public address (falls back to `127.0.0.1`). New `scripts/artifact_host.py`; `url_gate.py` accepts that host and rejects loopback-only replies when set; unset is unchanged. `install-global --artifact-host VALUE` persists it in each Claude `settings.json` `env`. Both always-on blocks reword the HTML line. Skill 2026.10.14.2.

## Unreleased — dispatch suffix always

- The machine-dispatcher bind suffix was often skipped (3 of 6 vps1 test threads, mostly bare greetings) and agents invented the name. The always-on block line now requires the env check (`echo "$EPICSPINE_DISPATCHER"`) on every thread's first turn, greetings included, then `status`, and the suffix `· dispatch: <status.name> (<status.available>/<status.capacity> seats)` with the name verbatim; rule 1 points to it. SKILL.md and `references/machine-dispatcher.md` match. Skill 2026.10.14.1.

## Unreleased — machine dispatcher

- Env `EPICSPINE_DISPATCHER` routes every manager's worker dispatch through one machine-level command (`status` / `pick` / `done`; `via`: `t3_delegate_task`), with no per-repo rule. The manager runs the command directly; repo `Dispatch profile: local-only` opts out; errors fall back to a native subagent. Both always-on blocks gain one line. Reference adapter: `examples/dispatchers/t3_seat_pool.py`.
- `install-global --config-dir DIR` (alias of `--claude-dir`) also links `<dir>/skills/epic-spine` to the installed skill; `check-global` reports it, `uninstall-global` removes only our link.

## Unreleased — URL gate

- `scripts/url_gate.py` is a Claude Code `Stop` hook that blocks a final reply naming an HTML/visual path or `file://` without a reachable `127.0.0.1`/`localhost` URL (max 2 blocks per turn, fail-open, `EPICSPINE_URL_GATE=off` disables). `install-global` registers it for Claude Code alongside the SessionStart hook (`--no-hooks` skips; `uninstall-global` removes only ours). The URL rule is now in both always-on blocks and the worker handoff requires `url`/`port`/`pid`.

## Unreleased — profile command

- `agents_block.py profile [--repo PATH]` prints the effective dispatch profile and source (exit 3 if unset); `profile --set "..."` writes the machine file.

## Unreleased — machine-wide dispatch profile

- The dispatch profile is set once per machine in `~/.agents/epicspine-profile.md` (survives upgrades); the repo `Dispatch profile:` line is now an optional override, and ask-once saves to the machine file.

## Unreleased — tree-based freshness

- `skill_update.py` decides freshness by the git tree hash of `skill/epic-spine/` (blobless clone), so docs-only commits no longer mark installs stale; the pin gains `tree:` and `latest:`, the cache returns the last verdict (stale stays stale), and the default window is 1 day. `upgrade` short-circuits when the tree is unchanged.
- The skill dir is symlink-resolved: harness symlinks to a non-git hub now work; `linked` means a git work tree or vendored copy.

## Unreleased — vanilla dispatch default

- The shipped default is now a lower-cost native subagent in its own worktree; no vendor, model ID, or T3/OpenCode is hardwired. With no root-spine `Dispatch profile:`, the agent asks once, recommends the default, and records the answer there; the recorded profile then wins. The Failure Rule is now generic.

## Unreleased — lean kernel

- Splits `SKILL.md` into a ≤ 150-line kernel — Overview, a 9-rule **Default Behaviors** card, Bind Path, a load-on-demand table, and spine document minimums — and moves every removed section verbatim into `references/spine-model.md`, `references/spine-creation.md`, `references/role-protocols.md`, `references/dispatch-prompts.md`, and `references/sprint-dialect-v2.md`. A cold agent now reads the kernel (491→65 lines, 7,134→687 words) and loads deeper references only when a task triggers them.
- Adds `references/artifacts.md`: serve HTML/visual artifacts from `127.0.0.1` and report a verified clickable `http://127.0.0.1:<port>/<file>` URL, never a file path or `file://`; workers hand back `url`/`port`/`pid`/`directory` and the manager relays the link.
- Adds `tests/test_budgets.py`: CI line budgets for `SKILL.md` (≤ 150), new references (≤ 200), pre-existing files (a rounded ratchet that may be lowered but raised only with a recorded reason), example `Operating Learnings` **Always** blocks (≤ 12), and a no-orphan check that `SKILL.md` links every skill file.
- README gains a short `Defaults` pointer to the kernel card instead of repeating the detail. `references/git-doctrine.md` Clean Repo Contract now applies "with no work in flight"; `assets/dispatch-prompt-preamble.md` flags HTML outputs as served URLs; `references/hygiene.md` notes a sweep stops artifact servers.

## Unreleased — skill self-update and freshness

- Adds `scripts/skill_update.py` (stdlib-only): `status` reports `fresh`/`stale`/`unpinned`/`unknown`/`linked` from a `<skill-dir>.SOURCE` pin, using one network check per window (default 7 days, no clone); `upgrade --yes` shallow-clones, verifies the tree byte-for-byte against `MANIFEST.sha256`, swaps atomically with one `.bak`, and rewrites the pin.
- Adds `references/skill-update.md` — the simple upgrade answer, status vocabulary, the `Skill updates: auto|manual|off` policy, the repo-level `EpicSpine skill:` record, vendored-copy handling, and the trust model.
- Adds `VERSION` (CalVer `YYYY.MM.DD`, bumped when a change lands on `main`; freshness is decided by commit and manifest, not the label).
- Adds the `## Skill Freshness` section to `SKILL.md` and `## Upgrading` to the README.
- Adds `tests/test_skill_update.py`, including a proof that the Python manifest equals `tools/epicspine-manifest.sh`.

## Unreleased — repo hygiene sweeps

- Adds a repo-hygiene protocol: the delivery manager removes a worker's worktree and local branch right after integrating, and dispatches a cheap **sweep** worker as backstop for what slipped through.
- Defines sweep triggers, three copy-paste checks, a merged/clean classification table, and strict safety rules: never force, never rewrite history, never touch `main`.
- Records one `Last sweep: YYYY-MM-DD, <result>` line in the root spine and reports to the user only when a decision is needed or more than 100 MB was reclaimed.
- Adds `references/hygiene.md` and `assets/sweep-brief.md`.

## Unreleased — operating learnings

- Adds **operating learnings**: one-line rules (`L-<n> | applies when | rule | why | confirmed date`) stored in the spine tree so a newly bound agent reads only what its task needs.
- Depth is scope: a root `## Operating Learnings` holds **Always** (read in full at bind, ≤ 12 lines) plus a **Scoped index** pointing to the branch spine or leaf that owns each scoped rule; branch spines hold their own.
- Agents report `Learnings in force:` at bind, may propose a learning (never write silently), and hand candidates back as `Learning candidates:`; only the spine steward writes, promotes, or prunes.
- Adds `references/learnings.md` and `## Operating Learnings` sections to both spine templates and the CLI/rollup examples.

## Unreleased — roles and dispatch profile

- Adds two base roles: **delivery manager** (dispatches workers, verifies their output, integrates, keeps spine/issue state, and reports; never implements) and **worker** (exactly one task, own worktree, structured handoff). Existing identities remain valid as specific remits under those roles.
- Adds the **dispatch profile** — mechanism, provider, model, reasoning, runtime mode, isolation (worktree-first), parallelism, and review — with a built-in T3 `delegate_task` default on the OpenCode provider and per-field overrides from plain user words or a `Dispatch profile:` declaration in the root spine or `AGENTS.md`.
- Reserves `Dispatch profile: template:<name>`; templates are not defined yet, so an unknown template stops and asks instead of guessing.
- Records the manager verification duty: check the repository, branch/diff, and checks independently, link any opened PR, and integrate verified work under the git doctrine.
- Adds `references/roles-and-dispatch.md` and optional `Dispatch profile:` lines in the dispatch preamble and both spine templates.

## Unreleased — git doctrine (stay in `main`)

- Establishes one integration line, `main`: the primary checkout always sits on a clean `main` and is never used to edit; worker changes live on short-lived local `wt/<task>` worktree branches.
- Adds `references/git-doctrine.md`: worker flow (local worktree branch, commit, hand off; no push or PR by default), manager integration flow (verify in the worktree, rebase if `main` moved, `git merge --ff-only`, refresh generated artefacts, push, test in `main`, remove the worktree and branch), rollback via `git revert` (never force-push `main`), serial integration, and the clean-repo contract.
- Replaces "merge without the user's approval" with a standing grant: the delivery manager merges verified work to `main` itself; approval is required only when the repo declares `Integration policy: pr-approval` or the user reserves it for a task.
- Makes pull requests optional (review request, repo declaration, or CI-gating), not default, and drops remote worker branches as the default.
- Adds optional `Integration policy: main-direct` lines and defaults `Integration branch: main` in both spine templates.

## Unreleased — EpicSpine v2 sprint dialect

- Encodes the 2026-07-10/11 production lessons: v1 consumed roughly 24 hours with zero human-testable output and an architecture crisis despite 1,100+ green tests; the v2 journey-first dialect shipped Zenod overnight and made Callisthenes, Ring, and Phylax dispatch-ready.
- Makes worker worktrees mandatory and bans shared-clone checkout (the observed “branch ransom” failure).
- Adds paste-ready dispatch prompts, ticket budgets, heartbeats, shouted Human Gates, pinned bases/lap limits, proportional ceremony, and earliest-touchable sequencing.
- Replaces flat property-checklist acceptance with live-browser SHIP journeys plus deferred HARDEN; records the blank-page incident behind “never ask the human to click the unclicked.”
- Adds port-first inventory and PORT/DUPLICATE/BUILD markings after the working customer layer was unnecessarily rebuilt while it already existed in `zenod-ai/cloud`.
- Keeps existing v1 spines compatible: new v2 validator rules emit warnings rather than errors.
