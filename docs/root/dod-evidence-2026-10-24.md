# EPIC-0 DOD-1 / DOD-2 evidence (2026-10-24)

Worker: test sub-agent, run_da93bbb6-1efe-4ea8-8e6c-e2ad2530ed08. Measured on main 83a424d (root spine counted at 259ed38, 153 lines). No spine edited.

## DOD-1 cold bind in three hops, ≲ 100 lines

Verdict: **not met as observed; met on the prescribed path.** Leave unticked until the gap below is closed (or the DOD is reworded to the prescribed-path measure).

Prescribed path (what the always-on block says: root spine "down to Operating Learnings only"), at 259ed38:

| Read | Lines |
|---|---|
| AGENTS.md (whole) | 16 |
| docs/EPIC-0-OPERATING-SYSTEM.md 1–62 (header, Current State, Mission, Non-Goals, Operating Learnings) | 62 |
| docs/EPIC-4-DOCTRINE-2.md `## Current State` (36–50), sample task | 15 |
| **Total** | **93** (79 non-blank) |
| + `assets/global-block.md` (16, SessionStart-injected; counts toward context) | 109 |

Observed (one fresh native subagent, no context, task "status + next action of EPIC-4", read-only). Its bind came from the injected global block + AGENTS.md; before its first non-read action it read three files **whole**:
global-block.md 17 lines, EPIC-0 spine 141 lines (the file was 141 then), EPIC-4 spine 124 lines = **282 lines** (+16 AGENTS.md from session context ≈ 298). It reached the right answer in 5 tool calls. It ignored "down to Operating Learnings only" because the Read tool returns whole files by default.
(`claude -p` cold run not possible: CLI is not logged in on seat1/seat2 — "Not logged in · Please run /login".)

Gap: the path is three hops and 93 lines on paper, but nothing makes an agent stop at line 62 or at the child's Current State, so real cold reads are ~2.8× the target. n=1.

Smallest concrete changes (pick one; trims alone cannot reach 100 for whole-file reads, since root is 153 lines and EPIC-4 124):
1. Bound the read where the agent looks: AGENTS.md EpicSpine block names the range ("read `docs/EPIC-0-…md` lines 1–62 only"); brittle but cheap, 1 line.
2. Move the tail of the root spine off it (Issue Ledger 27 lines, Decisions 25, Book Companion 23 → pages under docs/root/, leaving one link line each): root becomes ≈ 80 lines, whole-file read ≈ 16 + 16 + 80 + 15 = 127; with Definition Of Done moved up below Operating Learnings the 1–62 cut also stays valid.
3. Trim on the prescribed path to leave headroom for the global block: delete the `L-15..L-17 superseded` line (root line 56) and fold Current State `Evidence` + `Approved work` (lines 22, 25) into one line each referencing steps.md: −3 lines (→ 90 / 106 with the block).

## DOD-2 lean kernel and installed copies re-synced

Verdict: **met.**

- SKILL.md: 72 lines, 13000 bytes (cap 150 in tests/test_budgets.py). `## Default Behaviors` is at lines 13–26: 10 numbered behaviors plus intro (cap ALWAYS_MAX 12).
- `python3 -B -m unittest tests.test_budgets`: 5 tests OK. Full suite: 655 tests OK (skipped=2).
- `tools/epicspine-manifest.sh skill/epic-spine` equals committed MANIFEST.sha256 (66 files); VERSION 2026.10.24.6.
- Installed copies on this machine (no ~/.codex, ~/.gemini, ~/.agents/skills, opencode, windsurf, copilot present):
  - `~/.claude_seat1/skills/epic-spine` and `~/.claude_seat2/skills/epic-spine` are symlinks to `/home/t3agent/github/epicspine-skill/skill/epic-spine`; manifest through the link matches MANIFEST.sha256.
  - Both seats' CLAUDE.md pointer block, SessionStart and Stop hooks are `current` (`agents_block.py check-global`); they point at the canonical checkout, so they cannot go stale.
  - `~/.agents/epicspine-profile.md` is identical to `assets/epicspine-profile.md`. Background sync cron is scheduled (15 min).
  - `~/.claude` (no `-seat`) holds only policy/session files, no skills, CLAUDE.md or hooks: `check-global` prints `missing` for it. No harness here uses it (seats set `CLAUDE_CONFIG_DIR`); nothing installed, so no stale copy. Not changed (new config there is outside the re-sync step).

Stale copies: none. Gap: none. Ordinary caveat: other machines (VPS1, agent_team vendored copies in `epicspine-vendored` stamps) were not inspected.

## DOD-1 re-measure after the bind trim (run_ebab293c, main after 41dec46 + AGENTS.md pointer)

Changes: root spine 141 → 99 lines (Decisions rows, 7 done ledger rows, Book Companion fields moved to `docs/root/{decisions,steps,book-companion}.md`, one link line each; `L-15..L-17 superseded` line dropped); AGENTS.md line 3 is an explicit bind instruction (`Read` offset 18 limit 45 for the root, `sed -n '/^## Current State/,/^## [^C]/p'` for the task epic), kept honest by `tests/test_bind_range.py`. Strict graph validation 0 errors; 656 tests OK.

Fresh native subagent, no context, same task ("status + next action of EPIC-4", read-only), three rounds as the pointer improved:

| Round | AGENTS.md pointer | Read before answering | Lines |
|---|---|---|---|
| 1 | in-block-adjacent line 10, "Read tool, not whole files", child via `grep` then Read | global-block whole 17 + EPIC-0 offset 18 limit 45 (**obeyed**) + EPIC-4 whole 125 | **187** |
| 2 | line 10, `sed` for child | global-block 17 + EPIC-4 whole 124 + EPIC-0 whole 99 (pointer **ignored**) | **240** |
| 3 | line 3, bold, imperative, root range + `sed` for child | global-block 16 + AGENTS.md 18 + EPIC-0 offset 18 limit 45 (45) + EPIC-4 `sed` Current State (15) = **94**; it then also printed EPIC-4 `## Outcome` (17) by its own choice to answer "status" = 111 | **94** bind / 111 with task detail |

Verdict: **met in the best observed run (94 ≤ 100), not guaranteed.** Before: 282 (root 141, EPIC-4 whole). After: 94–111 when the pointer is followed, 187–240 when an agent ignores it (whole-file floor is now root 99 + child ~125 + block 16 + AGENTS 18 ≈ 258, so ranges, not size, carry DOD-1). n=3, one run per configuration; round 2 shows the pointer is advisory and position-sensitive (line 3 worked, line 10 did not once).

Recommendation (skill change, out of scope here): make the shared global block's bind step say "read Current State and Learnings with offset/limit, never whole spine files" and ship a `spines.py --bind <epic>` that prints only the chain's Current State + Operating Learnings, so every repo gets the bounded read without a repo-specific pointer.
