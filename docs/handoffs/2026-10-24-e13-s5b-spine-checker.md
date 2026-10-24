# E13-S5b brief: spine checker advisories for the status model (from agent_team EPIC-13)

Bound epic: docs/EPIC-0-OPERATING-SYSTEM.md (this repo). Origin: agent_team docs/spines/epic-13-one-status-model.md, step E13-S5 (part b); design deck http://100.86.141.63:58213/index.html slide 9. Independent: no dependency on the console work.

## Why (Jordi 2026-10-24)
The console's status is only as true as the spines behind it. Three spine shapes made it lie: free-text asks (zenod-social EPIC-0 showed a red Waiting-on line naming Jordi beside 'Waiting on you 0'); 'Status: done' with unticked Done means (this repo's EPIC-1 is flagged 'marked done while something under it is not green'); 'nothing open for Jordi' printed beside an open coded ask (infra-vps EPIC-2 showed it red).

## Build
In `skill/epic-spine/scripts/validate_spine.py` (advisory level, with `--strict` promoting them), add:
1. A `## Waiting on` line, or an open ledger row whose Owner is Jordi, that names him with no coded ask line (`[ask <CODE>: decide|approve|provide|do @Jordi since <date> row <id>]`).
2. `Status: done` (spine or ledger row) while any Done-means box is unticked.
3. `Waiting on:` saying nothing is open for Jordi while an open coded ask exists in the same spine (contradiction).
4. Update `references/` (spine-model.md / role-protocols.md ask-format section) and the dispatch/worker prompt snippets so the ask format and the three rules are shown once, briefly; keep `assets/global-block.md` size unchanged unless a line is replaced.

## Tests
One fixture spine per advisory (positive and negative) beside the existing validator tests (find them with `grep -rl validate_spine skill/epic-spine/tests`); the existing suite stays green; run the validator over this repo's own spines and agent_team's `docs/spines/*.md` and report the new advisories it raises (do not fix those spines here).

## Deliver
Integration policy main-direct, Skill updates auto: small commits, push to main, tests green (revert on red); report the commit SHAs and the advisory counts on agent_team's spines. Finish the step in this turn. Then write the SHA into agent_team docs/spines/epic-13-one-status-model.md E13-S5 Latest Evidence.
