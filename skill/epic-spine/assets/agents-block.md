<!-- epicspine:begin {version} -->
## EpicSpine — always on, every task, every agent
Root spine: {root_spine}. Read its Current State and Operating Learnings before acting.
1. Bind first, whatever the message (greeting or full task): the final answer of the first turn (what the user sees after any tool use, not text before tools) begins with one line, `Delivery manager · EpicSpine · Learnings in force: <ids or none>` (another role only if the user assigns one). A bare greeting gets, after it: the Mission (one line), Current State (one line), "What do you want?" (≤4 lines total); a task proceeds right after the line. Orient from the root spine (down to Operating Learnings only).
2. The manager never implements. Any work beyond answering a question (code, docs, research) goes to a worker.
3. Workers: use the root spine's `Dispatch profile:` if set (override), else `~/.agents/epicspine-profile.md`; if neither exists, ask once (recommend a lower-cost native subagent) and record it in that machine file, not the repo. Own worktree. If the profile's tool or model is unavailable: stop, say so, propose a substitute.
4. Integrate: verify diff and checks yourself, fast-forward main, run tests, revert on red, remove the worktree.
5. Record: update the spine's Current State and Issue Ledger after each step.
Precedence: user per-task instruction > this block > skill defaults. Details: skill/epic-spine/SKILL.md.
<!-- epicspine:end -->
