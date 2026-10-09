# AGENTS.md

Public EpicSpine skill source: `skill/epic-spine/` is canonical and deployed continuously from `main`.

START HERE: [docs/EPIC-2-OPERATING-SYSTEM.md](docs/EPIC-2-OPERATING-SYSTEM.md) is the root spine; follow its Spine Map to the branch matching your task.
Dispatch profile: default
Integration policy: main-direct
Skill updates: auto
Standing behaviors: read the Default Behaviors card in `skill/epic-spine/SKILL.md`.

Validate: `python3 -B skill/epic-spine/scripts/validate_spine.py --strict <spine>` (add `--graph` for the family); test: `python3 -B -m unittest discover -s tests`; after skill changes: `tools/epicspine-manifest.sh skill/epic-spine > MANIFEST.sha256`
