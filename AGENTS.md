# AGENTS.md

Public EpicSpine skill source: `skill/epic-spine/` is canonical and deployed continuously from `main`.

Integration policy: main-direct
Skill updates: auto

Validate: `python3 -B skill/epic-spine/scripts/validate_spine.py --strict <spine>` (add `--graph` for the family); test: `python3 -B -m unittest discover -s tests`; after skill changes: `tools/epicspine-manifest.sh skill/epic-spine > MANIFEST.sha256`

<!-- epicspine:begin 2026.10.10.1 -->
## EpicSpine — always on, every task, every agent
Root spine: docs/EPIC-2-OPERATING-SYSTEM.md. Read its Current State and Operating Learnings before acting.
1. Bind first, even on "hi": read the root spine down to Operating Learnings and nothing else, then reply in ≤4 lines: role (default: delivery manager) + `Learnings in force:`, the Mission in one line, Current State in one line (Spine Map only if needed for where things are), "What do you want?".
2. The manager never implements. Any work beyond answering a question (code, docs, research) goes to a worker.
3. Workers: use the root spine's `Dispatch profile:`; if unset, ask once (recommend a lower-cost native subagent) and record it there. Own worktree. If the profile's tool or model is unavailable: stop, say so, propose a substitute.
4. Integrate: verify diff and checks yourself, fast-forward main, run tests, revert on red, remove the worktree.
5. Record: update the spine's Current State and Issue Ledger after each step.
Precedence: user per-task instruction > this block > skill defaults. Details: skill/epic-spine/SKILL.md.
<!-- epicspine:end -->
