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

## Outcome

Added per node by step 10 (Outcome before close). `outcome` is `null` when the epic has no `## Outcome` section. Until the release ships the field is absent: fall back to Done means + Status.

```json
"outcome": {
  "verdict": "accomplished | partially accomplished | not accomplished | superseded",
  "sentence": "one sentence: what was achieved",
  "evidence": [{"done_means": "E4-1 New epics follow the doctrine by default", "links": ["https://github.com/o/r/pull/31", "0891cbb"]}],
  "risk": "residual risk / follow-ups, or null",
  "closed_at": "2026-10-20",
  "closed_by": "EPIC-4 delivery manager (thread mcp:...)"
}
```

The section in the spine it is read from:

```markdown
## Outcome

Verdict: accomplished
Outcome: <one sentence>
Closed: 2026-10-20 by <agent / run>
Risk: <residual risk and follow-ups, or none>

| Done means | Evidence |
|---|---|
| E4-1 New epics follow the doctrine by default | [PR #31](https://github.com/o/r/pull/31), 0891cbb |
```

- `links` keeps each comma-separated item of the Evidence cell; a Markdown link gives its target. Items may be URLs, commit SHAs, `PR #n`, or repo paths.
- `risk` is `null` when the line says `none`. Any field not written is `null` (`evidence` is `[]`).
- The console shows an Outcome card (verdict, sentence, evidence per Done means, risk, closed) for any epic whose `outcome` is not null; the parent's rollup cites `sentence`.

## Latest state

Added per node by step 11. The console's top card shows the Outcome when there is one, and otherwise this. Each key is the snake_case form of its `## Current State` label. A label that is missing or empty gives `null`; `current_state` is `null` when the section is absent.

```json
"current_state": {
  "status": "active",
  "last_attempted": "2026-10-19 root swap merged (ef15cfa); ...",
  "result": "step 7 done; ...",
  "evidence": "main ef15cfa; ...",
  "waiting_on": "Jordi's approval ...",
  "next_action": "Jordi approves the doctrine page ...",
  "verified_at": "2026-10-19"
}
```

- Values are the raw line text after `Label:`. `status` is the same value as the node's existing `status`.
- Stale flag (the console's call): Current State is stale when `verified_at` is older than the epic's last run. The doctrine has the manager refresh Last attempted, Result, Waiting on, Next action and Verified at at the end of every working session or wake.

## Waiting on

Added per node by step 12. `waiting_on` lists the structured asks under the epic's `## Waiting on` section, `[]` when there are none. Each item is `{who, ask, question, options, recommend, context, since, row, state, answer}`; `state` is `open` or `answered`, `answer` is null while open, `context` is repo-relative for a local link and an external URL is kept as-is. An `answered` line keeps only `who`, `question`, the fields it still carries and `answer` (`ask`, `since` and `row` are null: the tag no longer holds them). The format, the answer write-back and the advisory checks are in [human-asks.md](human-asks.md).
