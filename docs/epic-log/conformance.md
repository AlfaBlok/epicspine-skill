# Conformance scan: before/after per repo

Page of [EPIC-3](../EPIC-3-EPIC-LOG.md) (E3-3). `spines.py --json` on every repo on vps1. Green = 0 orphans, 0 mismatches, `looks_like_epic` resolved or recorded; orphan pages are advisory. Raw: [scan-2026-10-22.tsv](scan-2026-10-22.tsv).

| Repo | Root | Nodes | Orphans | Mismatches | Looks like epic | Orphan pages | After |
|---|---|---|---|---|---|---|---|
| poly-maker | EPIC0.md | 55 | 3 | 0 | 14 | 343 | green: 58 / 0 / 0 / 14 recorded as exceptions ([list](https://github.com/AlfaBlok/poly-maker/blob/main/docs/spines/LOOKS_LIKE_EPIC_EXCEPTIONS.md)) / 339 (1dc21c66..69a3a0d8) |
| zenod | docs/EPIC-0-FOUNDATION-SPINE.md | 4 | 0 | 0 | 28 | 140 | green: 29 / 0 / 0 / 3 recorded as exceptions / 104 (PR #1420, merge 2c34984); 7 superseded goals closed, 6 flagged stale for the owner |
| infra-vps | docs/EPIC-0-VPS-FLEET.md | 7 | 0 | 0 | 39 | 16 | green: 7 / 0 / 0 / 41 recorded as exceptions / 3 (e991032..5f0ab65); Serves added to 6 epics; E5 and tailscale-only-vps1 flagged as promotion candidates for Jordi |
| tax-assist-research | docs/EPIC_SPINE.md | 18 | 0 | 4 | 0 | 552 | green: 18 / 0 / 0 / 0 / 553 (8cebb7b): a misplaced P3 header, 2 Spine Map rows |
| abnb-agent | docs/travel/TRAVEL_SPINE.md | 1 | 0 | 0 | 4 | 18 | green: 3 / 0 / 0 / 2 recorded as exceptions / 6 (585732d); root kept (travel home); EPIC-1 Pyrenees dormant since 2026-08, left for Jordi |
| agent_team | yes | 5 | 0 | 0 | 0 | 12 | green |
| house_decision | yes | 1 | 0 | 0 | 0 | 20 | green |
| sismic | yes | 1 | 0 | 0 | 0 | 3 | green |
| testaments | yes | 1 | 0 | 0 | 0 | 0 | green |
| epicspine-skill | yes | 5 | 0 | 0 | 0 | 2 | green |
| idea_scraper | none | - | - | - | - | - | A1 `all`: root in progress (mcp:908a8617) |
| obsidian-brain | none | - | - | - | - | - | A1 `all`: root in progress (mcp:ae7b32be) |
| zenod-cloud | none | - | - | - | - | - | A1 `all`: root in progress (mcp:df6f29ed) |
| nectary | none | - | - | - | - | - | A1 `all`: root in progress (mcp:b3711a17) |
| zenod_memory | none | - | - | - | - | - | A1 `all`: root in progress (mcp:377938ea) |
| alpha9_webflow_export | none | - | - | - | - | - | A1 `all`: root in progress (mcp:ca22629c) |

Before = 2026-10-22 (skill 2026.10.22.5). The 2026-10-19 r1 counts used the pre-Doctrine-2 orphan definition and are in [the handoff](../handoffs/2026-10-19-spine-conformance.md).
