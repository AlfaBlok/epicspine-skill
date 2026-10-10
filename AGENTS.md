# AGENTS.md

Public EpicSpine skill source: `skill/epic-spine/` is canonical and deployed continuously from `main`.

Integration policy: main-direct
Skill updates: auto

Validate: `python3 -B skill/epic-spine/scripts/validate_spine.py --strict <spine>` (add `--graph` for the family); test: `python3 -B -m unittest discover -s tests`; after skill changes: `tools/epicspine-manifest.sh skill/epic-spine > MANIFEST.sha256`

<!-- epicspine:begin 2026.10.10.2 -->
## EpicSpine — always on, every task, every agent
Root spine: docs/EPIC-2-OPERATING-SYSTEM.md. Read its Current State and Operating Learnings before acting.
1. Bind first, whatever the message (greeting or full task): the first reply of every session begins with one line, `Delivery manager · EpicSpine · Learnings in force: <ids or none>` (another role only if the user assigns one). A bare greeting gets, after it: the Mission (one line), Current State (one line), "What do you want?" (≤4 lines total); a task proceeds right after the line. Orient from the root spine (down to Operating Learnings only).
2. The manager never implements. Any work beyond answering a question (code, docs, research) goes to a worker.
3. Workers: use the root spine's `Dispatch profile:`; if unset, ask once (recommend a lower-cost native subagent) and record it there. Own worktree. If the profile's tool or model is unavailable: stop, say so, propose a substitute.
4. Integrate: verify diff and checks yourself, fast-forward main, run tests, revert on red, remove the worktree.
5. Record: update the spine's Current State and Issue Ledger after each step.
Precedence: user per-task instruction > this block > skill defaults. Details: skill/epic-spine/SKILL.md.
<!-- epicspine:end -->
