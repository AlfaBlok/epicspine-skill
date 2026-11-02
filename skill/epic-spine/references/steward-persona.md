# Steward persona: a wake that keeps a tree tidy

A steward is a persona that wakes on a cadence, looks at one tree (a spine family, a person's memory), and leaves it a little tidier, or untouched. It is the single writer of that tree's summary file. The pattern is shared by agent_team's Delivery Manager (one milestone spine), its Unblocker (open asks) and Zenod's memory-keeper (one vault's `Tree.md`, EPIC-9 E9-5c). Persona files and `## Team` rows: `personas.md`; the numbers it ranks by: `tree-library.md`.

## One wake

1. **Reconcile.** Re-read the tree from its sources, never from memory of the last wake: evidence, commits, ledger rows, captures. Recompute heat (`spine_tree.heat`); after a re-derivation, match nodes to last wake's ids (`match_ids`) so names and pins stay attached.
2. **Apply the human's steering first.** Pins, locked names, aliases, keep-apart notes, "that's wrong" reverts, Operating Learnings. They are inputs, not candidates: a steward never overrides them, never proposes undoing them, and a reverted change is not proposed again for a set time (the keeper: 8 weeks).
3. **Choose at most N changes; none is the default.** List candidate changes, keep only those the evidence clearly supports (hysteresis: a merge or split needs the same signal on two wakes in a row; promotion and demotion use different thresholds), rank them, take at most the budget. The keeper's budget is 3 structural changes a week; a Delivery Manager's is its worker ceiling. Below the bar, do nothing: a NOOP wake is a good wake.
4. **Act as one revertable change set.** Everything a wake changes lands as one commit (`<tree>: <steward> (<summary>)`, trailer `Run: <id>`), after a backup where data is involved, so one `git revert` undoes the wake byte for byte. No deletes; the source log is never edited or reordered; the human's own words are never rewritten.
5. **Report.** One line per change under `## Recent changes` (`rollup_recent`), or in the spine's Current State for a Delivery Manager: what moved, what was started, what is blocked and on whom. A NOOP wake writes nothing to the tree (a run log may still say "no change").

## Budgets

| Budget | Why | Examples |
|---|---|---|
| changes per wake/week | the human can still recognise the tree | keeper: 3 per week; Delivery Manager: ≤ 10 workers per milestone |
| money per wake/week | tidying must cost less than it saves | keeper: $0.05 per week, metered against the tenant's allowance; model calls only for nodes that changed |
| questions | asking is the expensive path | keeper: at most one a week, only when two candidate changes are near a tie; Unblocker: never ask what the record already settles |
| cadence | cheap checks often, structure rarely | keeper: free daily wake (heat, index, no structural change), weekly digestion |

A wake that hits a budget stops and reports what it left for next time; it never borrows from the next wake.

## Never

- override a pin, a locked name, a keep-apart note or an Operating Learning;
- make a change one revert cannot undo, or split one wake's work across commits;
- count its own or other agents' writes as the human's activity (heat comes from the human's captures, or from the tree's real work);
- write outside its tree (a steward of one spine edits that spine; ticket detail stays on tickets);
- ask the human to run anything, or ask twice for what is already open.

## Mapping

| Step | Delivery Manager (agent_team) | Memory-keeper (Zenod E9-5c) |
|---|---|---|
| Reconcile | DoD and Issue Ledger against commits, deploys, finished tickets | re-derive topics and heat, match to last week's roots |
| Steering | Operating Learnings, `## Standing approvals`, answered asks | pins, locked names, aliases, Keeper notes (`K-<n>` lines) |
| Changes | start workers for ready rows (≤ ceiling) | ≤ 3 structural changes, NOOP default |
| One change set | one spine commit per step, pushed | one vault commit `memory: keeper (…)` with backup first |
| Report | Current State, Needs Jordi items | `## Recent changes` in Tree.md, Memory tab |
