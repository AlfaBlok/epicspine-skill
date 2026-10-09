# Changelog

## Unreleased — roles and dispatch profile

- Adds two base roles: **delivery manager** (dispatches workers, verifies their output, integrates, keeps spine/issue state, and reports; never implements) and **worker** (exactly one task, own worktree, structured handoff). Existing identities remain valid as specific remits under those roles.
- Adds the **dispatch profile** — mechanism, provider, model, reasoning, runtime mode, isolation (worktree-first), parallelism, and review — with a built-in T3 `delegate_task` default on the OpenCode provider and per-field overrides from plain user words or a `Dispatch profile:` declaration in the root spine or `AGENTS.md`.
- Reserves `Dispatch profile: template:<name>`; templates are not defined yet, so an unknown template stops and asks instead of guessing.
- Records the manager verification duty: check the repository, PR, and CI independently, link every opened PR, and merge only with the user's approval unless granted.
- Adds `references/roles-and-dispatch.md` and optional `Dispatch profile:` lines in the dispatch preamble and both spine templates.

## Unreleased — EpicSpine v2 sprint dialect

- Encodes the 2026-07-10/11 production lessons: v1 consumed roughly 24 hours with zero human-testable output and an architecture crisis despite 1,100+ green tests; the v2 journey-first dialect shipped Zenod overnight and made Callisthenes, Ring, and Phylax dispatch-ready.
- Makes worker worktrees mandatory and bans shared-clone checkout (the observed “branch ransom” failure).
- Adds paste-ready dispatch prompts, ticket budgets, heartbeats, shouted Human Gates, pinned bases/lap limits, proportional ceremony, and earliest-touchable sequencing.
- Replaces flat property-checklist acceptance with live-browser SHIP journeys plus deferred HARDEN; records the blank-page incident behind “never ask the human to click the unclicked.”
- Adds port-first inventory and PORT/DUPLICATE/BUILD markings after the working customer layer was unnecessarily rebuilt while it already existed in `zenod-ai/cloud`.
- Keeps existing v1 spines compatible: new v2 validator rules emit warnings rather than errors.
