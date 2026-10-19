# Console contract: `spines.py --json` doctrine fields

Page of [EPIC-4](../EPIC-4-DOCTRINE-2.md), steps 3 (producer) and 4 (agent_team console).

Run it as `python3 <skill>/scripts/spines.py --json --repo <repo>`. Today's output stays valid. The fields below are **added**, and all existing fields keep their meaning:
- top level: `root`, `nodes[]`, orphans;
- per node: `id`, `path`, `title`, `parent`, `status`, `rollup_status`, `dod`, `children[]` (paths);
- `type` is deprecated: the root is the node with `parent: null`.

## Added per node (each epic)

```json
{
  "goal": "plain words: what and why (from ## Goal or ## Mission), or null",
  "serves": "how it serves its parent (from ## Serves), or null; null for the root",
  "done_means": [{"id": "DOD-1", "text": "...", "done": false}],
  "contributes": {"docs/EPIC-3-EPIC-LOG.md": "one sentence: what this child adds to this goal"},
  "pages": [{"path": "docs/doctrine/enforcement.md", "title": "Doctrine enforcement plan", "via": "docs/EPIC-4-DOCTRINE-2.md"}],
  "missing_sections": ["serves"],
  "size": {"lines": 120, "long_cells": 3}
}
```

- `done_means` reads `## Done means`, falling back to the DoD heading. It has the same shape as `dod`.
- `contributes` is keyed by child path, read from this epic's Spine Map. A child without a sentence is absent from it.
- `pages` lists the unstamped docs reachable by links from this epic, at any depth, through other pages. A page may appear under several epics. `via` is the leaf that links it.
- `missing_sections` uses these names: `title`, `goal`, `serves`, `done_means`, `status`.

## Added at top level

```json
{"orphan_pages": ["docs/old-notes.md"], "looks_like_epic": ["docs/some-page.md"]}
```

## What the console shows (Overview of an epic)
1. Title and Status.
2. Goal.
3. The Serves chain: walk `parent` up to the root and show each ancestor's `serves`.
4. The children, each with its `contributes` sentence and status.
5. Done means, as checkboxes, above the steps.
6. Pages.
7. Then the steps/tickets as today.

If `missing_sections` is non-empty, show a quiet "not yet compliant: <names>" note. Code against these fields now. Before the tools release, a missing field means "not provided yet", so render nothing for it and never fail.

## Agent pipeline check (also step 4)
A persona launched from the console must receive the EpicSpine always-on block (SessionStart hook) and bind to its epic. Verify this on one live launch.
