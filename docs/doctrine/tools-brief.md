# Step 3 tools brief (worker spec)

Page of [EPIC-4](../EPIC-4-DOCTRINE-2.md), step 3. This is a spec page, not a goal. It is sent as the worker brief once Jordi approves and EPIC-3 E3-2 is on main.

**Base:** main after E3-2. `spines.py` has 166 lines against a 200-line budget; it also has a helper, `epic_log.py`. Put the new parsing in a new helper, `scripts/doctrine.py`, and name it in SKILL.md's "Creating a spine" row, because test_budgets requires every skill file to be named in a SKILL.md row.

**Build** (follow [enforcement.md](enforcement.md) and [console-contract.md](console-contract.md) exactly):
1. **`spines.py --json`:** add these fields per epic, without changing any existing field:
   - `goal`, `serves`, `done_means` (`## Done means`, falling back to the DoD heading);
   - `contributes` (keyed by child path, from the Spine Map);
   - `pages` (follow inbound links from epics through pages, any depth; `via` is the linking leaf);
   - `missing_sections` (title, goal, serves except root, done_means, status);
   - `size` {lines, long_cells > 200 chars}.

   At top level, add:
   - `orphan_pages`: docs no tree leaf links to (same skip list as today);
   - `looks_like_epic`: pages containing Goal / Done means / checkbox outcomes / Next action / Status.
2. **Epic detection:** only `EPIC-<n>`-stamped docs, or docs with a `Spine ID:`, are epics. A file named `*PLAN*` is no longer an epic by name alone. A page called `enforcement-plan.md` was blocked on 2026-10-19.
3. **`spine_new.py`:**
   - write the `EPIC-<n>: <name>` title (next code from E3-2), Goal, Serves (with a parent link), Done means (2-5 checkbox placeholders, above the steps), Current State with `Status: ready`, the steps ledger, Decisions and Learnings;
   - add a contributes sentence placeholder in the parent's Spine Map;
   - write no `Spine Type:` line and no version line.
4. **`pre_commit.py`:**
   - BLOCK only a newly added epic that has a `missing_sections` entry;
   - for existing epics, give advisory warnings: missing sections, over 150 lines or long cells, `looks_like_epic` pages, orphan pages;
   - `--strict` stays advisory.
5. **`validate_spine.py`:** `Spine Type:` is no longer required (ignored if present).
6. **Templates:** `assets/epic-spine-template.md` and `assets/compact-spine-template.md` must match the scaffold. Drop `Spine Type: branch`.
7. **Reference trims:** trim duplicates of the doctrine page (operating-model.md Write Scope/Authority; ticket-backends.md vs "the step row is the ticket"). Net skill line count must not grow.

**Checks:**
- unit tests for each field, the new-epic block, the old-epic pass, orphan/looks-like flags, and `*PLAN*` pages;
- full suite green (load-flaky sync tests: rerun alone);
- `spines.py --json --repo .` on this repo shows EPIC-4's goal, serves, done_means and pages.

**Release:** CHANGELOG, VERSION bump, MANIFEST regenerated from a clean tree (no `__pycache__`). Add `Ready: yes`.

**Handover notes (EPIC-3, 2026-10-19, main 7f9643c):**
- E3-2 is merged, and the three tool files now belong to EPIC-4.
- `scripts/epic_log.py` already provides rollup, `--active`, stale, the next code and render. Put page discovery there or in `spines.py`.
- `background_sync.py` now has a `stale` field per repo.
- Guard `pre_commit.goal_notes`: a `Superseded by:` link that points outside the repo raises in `Path.relative_to`.
- Rule 6 of global-block.md already carries the record behaviours and the living-tree rules: `Goal: EPIC-<n>` per ask, close or supersede, stale after 14 days, a warning when Current State passes 12 lines. Do not restate them.
- Run tests only with an isolated config env until step 9 merges: `env CLAUDE_CONFIG_DIR=$(mktemp -d) CODEX_HOME=$(mktemp -d) XDG_CONFIG_HOME=$(mktemp -d)`.
