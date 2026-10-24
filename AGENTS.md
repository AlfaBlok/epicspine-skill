# AGENTS.md

**Bind: do not Read whole spine files** (Read returns every line). Root: `Read docs/EPIC-0-OPERATING-SYSTEM.md` offset 18 limit 45. Task epic: Bash `sed -n '/^## Current State/,/^## [^C]/p' docs/EPIC-<n>-*.md`. (`tests/test_bind_range.py` keeps the root range covering Operating Learnings.)

Public EpicSpine skill source: `skill/epic-spine/` is canonical and deployed continuously from `main`.

Integration policy: main-direct
Skill updates: auto

Validate: `python3 -B skill/epic-spine/scripts/validate_spine.py --strict <spine>` (add `--graph` for the family); test: `python3 -B -m unittest discover -s tests`; after skill changes: `tools/epicspine-manifest.sh skill/epic-spine > MANIFEST.sha256`

<!-- epicspine:begin repo-1 -->
## EpicSpine — always on, every task, every agent
Root spine: docs/EPIC-0-OPERATING-SYSTEM.md. Read its Current State and Operating Learnings before acting.
Shared EpicSpine rules (bind, dispatch, integrate, links) come from the epic-spine skill's always-on block, injected each session; if it was not, read `assets/global-block.md` in the skill dir (usually `~/.agents/skills/epic-spine`).
Repo values (`Dispatch profile:`, `Integration policy:`, `Skill updates:`) in the root spine or AGENTS.md override skill defaults.
Precedence: user per-task instruction > repo values > skill block.
<!-- epicspine:end -->
