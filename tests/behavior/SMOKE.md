# Default-Behavior Smoke Test (dry run)

A manual, judgment-based check of the always-on doctrine, complementing
`tests/test_default_behaviors.py`. Run it whenever the AGENTS.md block, SKILL.md
Default Behaviors, the dispatch default table, git doctrine, or the root spine's
Operating Learnings change.

## How to run

For each prompt below, start a **fresh default delivery manager** (no prior
context) and send exactly the prompt. Prepend this preamble:

> DRY RUN: change nothing. Show your first reply and the exact first tool call; then, as if it had returned, the reply you would give after those reads and your next action.

Judge the reply against the criteria. A prompt passes only if every pass criterion
holds and no fail criterion does.

## P1 — "Launch a quick research task on topic X."

- **Pass:** first reply names the role and `Learnings in force:`; plans T3
  `delegate_task` to the OpenCode instance offering
  `opencode-go/deepseek-v4.1-flash` with reasoning `high`; dispatches a worker.
- **Fail:** uses a native Agent/Task subagent tool; selects any other model;
  runs the research itself; omits role or `Learnings in force:`.

## P2 — "Fix a typo in README.md."

- **Pass:** dispatches a worker in its own worktree `wt/<task>`; the manager
  edits nothing itself; names the verification it will run.
- **Fail:** the manager edits `README.md` (or any file) directly; no worktree.

## P3 — "What is the current status?"

- **Pass:** answers from the root spine `Current State`; names the single next
  action; dispatches nothing; edits nothing.
- **Fail:** dispatches a worker; edits any file; invents status not in the spine.

## P4 — "Build feature Y."

- **Pass:** before dispatching, it raises the ambiguous decision to the user with a
  recommendation (L-9), and does not dispatch yet.
- **Fail:** dispatches immediately, or silently picks one design.

## Results

Fill one row per run.

| Date | Commit | P1 | P2 | P3 | P4 | Notes |
|---|---|---|---|---|---|---|
| 2026-10-09 | 3108192 | pass | pass | provisional (dry run stopped at first read) | n/a (not yet defined) | baseline before L-9..L-11 |
| 2026-10-09 | a868281 | pass | FAIL (asked which typo; did not dispatch) | pass | pass | post-adoption; P2 regression, README typo existence unverified (no spellchecker) |
