# Conformance scan: before/after per repo

Page of [EPIC-3](../EPIC-3-EPIC-LOG.md) (E3-3). `spines.py --json` on every repo on vps1. Green = 0 orphans, 0 mismatches, `looks_like_epic` resolved or recorded; orphan pages are advisory. Raw: [scan-2026-10-22.tsv](scan-2026-10-22.tsv).

| Repo | Root | Nodes | Orphans | Mismatches | Looks like epic | Orphan pages | After |
|---|---|---|---|---|---|---|---|
| poly-maker | EPIC0.md | 55 | 3 | 0 | 14 | 343 | green: 58 / 0 / 0 / 14 recorded as exceptions ([list](https://github.com/AlfaBlok/poly-maker/blob/main/docs/spines/LOOKS_LIKE_EPIC_EXCEPTIONS.md)) / 339 (1dc21c66..69a3a0d8) |
| zenod | yes | 4 | 0 | 0 | 28 | 140 | migrating (mcp:aa9a971f) |
| infra-vps | docs/EPIC-0-VPS-FLEET.md | 7 | 0 | 0 | 39 | 16 | migrating (mcp:51557bfc) |
| tax-assist-research | yes | 18 | 0 | 4 | 0 | 552 | queued |
| abnb-agent | yes | 1 | 0 | 0 | 4 | 18 | queued |
| agent_team | yes | 5 | 0 | 0 | 0 | 12 | green |
| house_decision | yes | 1 | 0 | 0 | 0 | 20 | green |
| sismic | yes | 1 | 0 | 0 | 0 | 3 | green |
| testaments | yes | 1 | 0 | 0 | 0 | 0 | green |
| epicspine-skill | yes | 5 | 0 | 0 | 0 | 2 | green |
| idea_scraper | none | - | - | - | - | - | EPIC-3-A1 |
| obsidian-brain | none | - | - | - | - | - | EPIC-3-A1 |
| zenod-cloud | none | - | - | - | - | - | EPIC-3-A1 |
| nectary | none | - | - | - | - | - | EPIC-3-A1 |
| zenod_memory | none | - | - | - | - | - | EPIC-3-A1 |
| alpha9_webflow_export | none | - | - | - | - | - | EPIC-3-A1 |

Before = 2026-10-22 (skill 2026.10.22.5). The 2026-10-19 r1 counts used the pre-Doctrine-2 orphan definition and are in [the handoff](../handoffs/2026-10-19-spine-conformance.md).
