# Tree library: heat, stable ids, Recent changes

Three small rules any self-tidying tree needs, whether the tree is a repo's spines or a person's memory. `scripts/spine_tree.py` implements them for EpicSpine; Zenod's memory tree (EPIC-9) ports them to TypeScript (`packages/core/src/engine/treeDiscover.ts`). Neither imports the other: this page is the contract, and `assets/tree-library-parity.json` holds inputs with expected outputs both sides test against. Change a rule here, in `spine_tree.py`, in the fixture and in the port together.

## Heat

A node's heat is how recently and how often it was worked, as one number that cools on its own:

`heat = Σ weight × 0.5 ^ (age_days / half_life)`, rounded half-up to 3 decimals (JavaScript `Math.round(x*1000)/1000`).

- `half_life` 14 days (`HALF_LIFE_DAYS`): an event today is 1.0, two weeks ago 0.5, four weeks ago 0.25.
- Events in the future (age < 0) or older than 120 days (`HORIZON_DAYS`) add nothing.
- `weight` defaults to 1; it is the share of the event the node holds (Zenod: a capture filed on two topics gives each its share).
- Age is whole UTC days between `YYYY-MM-DD` dates.

Heat replaces a yes/no "stale after 14 days" flag where a ranking is wanted: a goal touched every day for a month is hotter than one touched once yesterday. The stale flag stays for its existing readers (`spines.py --json` `stale`, the background `attention:` line).

Hysteresis belongs to the caller, not the library: Zenod promotes a topic to working memory at heat 0.9 and demotes it below 0.3, so the tree does not flap week to week.

## Spine heat (`spines.py`)

`spine_activity()` counts three sources per spine, each as **distinct days** (a burst of ten commits in a day weighs like one active day per source), and adds their heats:

1. commits touching the spine file (committer date; one `git log` per scan for all spines);
2. dates written in Current State `Last attempted:` (its "before: …" history included);
3. one day per Issue Ledger row: the latest date in the row.

`spines.py --active` lists open goals hottest first (ties keep tree order), each line ending `— heat <h>`; the fields before it are unchanged. `spines.py --json` adds per node `heat` and `last_activity` (latest day of any source, or null) and top-level `ranked` (open goal paths, hottest first). A git failure only drops source 1.

## Stable ids

When a tree is re-derived from content (clustering), its nodes come out as fresh member sets. To keep names, pins and history attached, each new set inherits the id of the old node it overlaps most:

- overlap is Jaccard, `|A ∩ B| / |A ∪ B|`; a match needs ≥ 0.5 (`MATCH_THRESHOLD`);
- matching is one-to-one and greedy, best overlap first; ties by old id, then by the new set's position (at ≥ 0.5 this agrees with an optimal assignment in practice);
- an unmatched set gets `n-` + the first 8 hex of sha1 over its sorted members joined by `\n`, with `-2`, `-3`, … if taken. Re-deriving the same content gives the same ids.

So a rename changes nothing (the members did not move), a node that lost one page of three keeps its id, a split keeps the id on the larger part, and a merge keeps the closer old id and retires the other.

## Recent changes

Between two derivations keyed by id (`{"name", "members", "kind"}`), `recent_changes()` reports, in this order and each sorted by id: `added`, `retired`, `renamed` (from → to), `moved` (kind from → to, e.g. working → long-term), `regrouped` (+gained −lost members). `rollup_recent()` renders them as bullets `- <day> · <text>`, newest first, ahead of the older lines, keeping 20. A run with no change leaves the section as it was: doing nothing is the default (see `steward-persona.md`).

## Where each piece is used

| Piece | EpicSpine | Zenod memory tree |
|---|---|---|
| Heat | `spines.py --active` ranking, `--json` `heat` | topic heat from the person's own captures (E9-2g) |
| Stable ids | not needed: spines have `Spine ID:` | root ids across weekly re-derivations (E9-5b) |
| Recent changes | a steward's report of its own tidy-ups | `## Recent changes` in Tree.md, shown in the Memory tab (E9-5c) |
