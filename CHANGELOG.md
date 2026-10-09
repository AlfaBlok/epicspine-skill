# Changelog

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
