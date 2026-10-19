# Handoff 2026-10-19: repos are "on latest EpicSpine" in name only

From: agent_team Delivery manager thread (32a5cd6f-a080-4a3f-a9c9-78454520cb3b), moved here by Jordi.
Owner from now: epicspine-skill Delivery manager.

## What Jordi expects (his words, binding)

A spine is anything that has to be done: a goal, an objective. It hangs from the root or from another spine. Every repo is on the latest EpicSpine, so every goal doc is a spine and shows up as one. Jordi has asked several times and was told it was all ready.

## What actually failed

"All repos on latest" was true only for the **installed parts**: the skill version, the hooks and the AGENTS.md block in each repo. It was never true for the **documents**. No step ever migrated or checked the existing goal docs, and nothing stops new ones from being written outside the format.

Trigger: poly-maker E4 (`docs/one-logger/E4-ONE-LOGGER.md`, created 2fdba07 on 2026-10-19) does not show in the agent_team console's milestone picker.
- It has no `Spine ID`, type, root or parent, no Current State, and no checkbox DoD. Its tickets are a table.
- It is not in a Spine Map. poly-maker's `EPIC0.md:174` lists it only as a ledger row.
- poly-maker's own root/hub (`EPIC0.md`, `EPIC.md`) has no `Spine ID` either, and agents copy the house style.
- The picker (`agent_team/console/server/src/adapters/repos.ts:163`) shows only `docs/spines/*.md`, `docs/EPIC-*.md`, `tickets/**`, or any file with a `Spine ID:` line. E4 matches none of these.

Root causes, in the skill:
1. **No migration of existing docs.** Rollouts updated AGENTS.md blocks only. `migrate_spine.py` and `spine_fix.py` exist, but were never run across repos.
2. **No creation path.** `references/spine-creation.md` is read only when an agent thinks it is "creating a spine". A planning session that writes "a plan + page" never triggers it.
3. **No enforcement.** `validate_spine.py` is opt-in. No Stop or pre-commit check flags a new goal doc without a spine header. M2-9 audit (2026-10-16): `--strict` fails 14 of 23 spines on vps1.
4. **No discovery contract.** Consumers (the console) guess spines from paths, because the skill gives them no "list this repo's spines" command.

## Repo scan, vps1, 2026-10-19 (read-only grep; `archive/` and `node_modules` excluded)

| Repo | Declared root spine | Docs with `Spine ID` | Epic/spine-named docs |
|---|---|---|---|
| abnb-agent | docs/travel/TRAVEL_SPINE.md | 0 | 3 |
| agent_team | docs/spines/root.md | 7 | 7 |
| alpha9_webflow_export | none | 0 | 0 |
| epicspine-skill | docs/EPIC-2-OPERATING-SYSTEM.md | 15 | 54 |
| house_decision | EPIC.md | 1 | 1 |
| idea_scraper | none | 0 | 24 |
| infra-vps | docs/EPIC-0-VPS-FLEET.md | 4 | 11 |
| nectary | none | 0 | 0 |
| obsidian-brain | none | 0 | 7 |
| poly-maker | EPIC.md | 5 | 39 |
| sismic | sismic.md | 1 | 0 |
| tax-assist-research | docs/EPIC_SPINE.md | 5 | 5 |
| testaments | docs/epic-spine/family-distance-epic-spine.md | 0 | 1 |
| zenod | docs/EPIC-0-FOUNDATION-SPINE.md | 6 | 79 |
| zenod-cloud | (no block) | 0 | 1 |
| zenod_memory | (no block) | 0 | 0 |

The "epic-named" count is a filename heuristic. Goal docs like E4 under arbitrary names are only partly counted, so the real gap is larger. Step 1 below measures it properly.

## What's left so every repo behaves as Jordi expects

1. **Define it in the skill.** A spine = any goal/objective doc. It must carry the v1 header (Spine ID, type, root, parent), Current State and a checkbox DoD, and it must be registered in its parent's Spine Map. Plan, proposal and epic docs are spines from their first commit.
2. **Scaffold.** Add a single command (e.g. `spine_new.py --parent <spine> --path <file>`) that writes a valid header and registers the new spine in the parent. Spine creation must use it.
3. **Enforce.** Add a pre-commit/Stop check: a new or changed goal doc (E<n>, EPIC, SPINE, PLAN, or any doc a spine links as a child) without a valid header gets flagged and blocked for agents. Gate on the narrow `trackable` check and keep `--strict` advisory (M2-9).
4. **Discover.** Add `spines --json --repo <dir>`, returning the spine tree from the root via Spine Maps plus unregistered goal docs flagged as orphans. The agent_team console picker switches to this (agent_team follow-up, after this ships).
5. **Audit and migrate every repo.** Run discovery across all 16 repos. Then, per repo, run one worker session (own worktree, per the repo's Integration policy and Deploy gate) that:
   - adds headers to root and child spines
   - registers children in Spine Maps
   - converts ticket tables to a checkbox DoD
   - adds a Current State where missing

   Start with poly-maker (E4, EPIC0.md, EPIC.md), then zenod, idea_scraper, infra-vps and abnb-agent. Repos with no root spine: offer one, don't force it.
6. **Prove it.** Publish a per-repo table: spines found, valid, orphans, plus the console picker showing poly-maker E4. Only then may anyone say "all repos on latest".
7. **Learning.** Add an Operating Learning in this repo: "on latest" means installed **and** docs conform (step 6 table green), never just the block version.

Constraints: poly-maker L-4 applies to implementation work, not to this docs migration, which Jordi ordered on 2026-10-19. poly-maker has an active one-logger session editing E4: coordinate with it, or do E4 last.
