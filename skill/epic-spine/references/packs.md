# Packs: typed vertical files a repo opts into

Base EpicSpine knows goals, state, ledgers, asks, learnings and the Team table; a repo may keep other files (`data/*.md`) but the base never says their shape. A **pack** says it for one vertical: the files, their sections and fields, the item lifecycles (statuses and legal transitions) and which persona role may write what, so personas, the commit-hook validator and the console screens agree on one shape. A pack is not a new spine type; spines stay as they are.

## What a pack is

`packs/<name>/` in the skill:

| File | Holds | Built in |
|---|---|---|
| `schema.json` | the machine-read schema: the one source every tool reads | E34-S1 |
| `README.md` | the human doc: files, statuses, who writes what | E34-S1 |
| `pack.py validate` (`scripts/pack_validate.py`, `pack_checks.py`) | checks a repo's files against the schema, in the commit hook too | E34-S2 |
| `pack.py init <name>` (`scripts/pack_init.py`) | creates the files with the right headings and columns | E34-S2 |
| `pack.py <name> --json` (`scripts/pack_export.py`) | exports the repo's typed data for the console, with computed back-links ("JSON export" below) | E34-S3 |
| `pack.py <name> --wake-text` (`scripts/pack_intake.py`) | the desk intake rule a desk persona's prompt carries ("Desk intake" below) | E34-S10 |

## Opt in

One line in the repo's `AGENTS.md` (repo values, outside the EpicSpine block): `Pack: social`. Several: `Pack: social, sales`. `EpicSpine packs: social` is read the same way. `python3 scripts/pack.py list --repo <path>` prints the packs a repo has on; without `--repo` it lists the packs the skill ships.

## Schema shape (`schema.json`)

- `pack`, `version`, `opt_in`, `owner` (the human role), `approval_gate` (`false`: the lifecycle `path` never waits on the owner), `roles` (role name → remit, one line).
- `files.<file>`: `path` (repo-relative; `{date}` + `many: true` for one file per item), optional `dir` (binary files), `sections`.
- `sections.<section>`: `heading` (the `## ` heading; `null` = the file's one table), optional `path` (a section kept in another file, e.g. the root spine's `## Goal`), `shape` (`text` | `list` | `table`), `writers` (roles; default for its fields), `add_rows` (roles that may add a row), `rows: "replace"` (the writer replaces the table each run), `fields`.
- `fields.<field>`: `column` (exact table header), `type` (`id` with `pattern`, `text`, `number`, `percent`, `bool`, `date`, `datetime`, `month`, `url`, `path`, `enum` with `values`, `role`, `ref`/`refs` with `ref: ["file.section", …]`), optional `writers` (overrides the section's), `computed: {from: "file.section.field"}` (derived by the export, nobody writes it), `lifecycle: <name>` (its values and writers come from that lifecycle).
- `lifecycles.<name>`: `field` (the status field it drives), optional `kind_field`, `initial`, `path` (the normal way through), `states` (state → meaning), `transitions` (`from`, `to`, `by` roles, optional `kinds`, `when`, `effect`). A status change not listed, or made by a role not in its `by`, is illegal.
- `intake` (optional): the desk-chat intake rule ("Desk intake" below).
- `effects` (what a transition does besides the cell), `rules` (cross-file automations, e.g. repeated feedback → a style rule), `checks` (what the validator runs, `at` the `from>to` transitions, with `params`).

Addresses are dotted: `file.section` and `file.section.field` (single-table files use section `rows`).

## Self-consistency

`python3 scripts/pack.py check [<name>]` (exit 1 on errors), used by `tests/test_packs.py`: every role named is in `roles`; every file, text section and non-computed field has a writer; every state is reachable from `initial`; every `path` step is a transition that some non-owner role can make when `approval_gate` is false; refs, `computed.from`, `kind_field`, effects, rules and check sources resolve; every `intake` target resolves and its kind's writer may write it. Add a pack by adding `packs/<name>/schema.json` and running `check`.

## Init

`python3 scripts/pack.py init social --repo <path>` writes each missing pack file from its sections' `heading` (`## …`) and the `column`s of their fields (heading `null` = the file's one table; `computed` columns are left out, the export derives them). It never overwrites: a file that exists only gains the sections it lacks, appended at its end; a missing spine (`docs/spines/…`, e.g. the brief's Goal/Targets in the root spine) is never created, only noted, and once it exists a rerun appends its missing headings; a file's `dir` gets a `.gitkeep`; per-item files (`many`, reports) are written by their persona. It adds `Pack: social` to AGENTS.md (creating it if needed) when absent. Idempotent: a second run prints `nothing to do`.

## Validate

`python3 scripts/pack.py validate [--repo <path>] [--staged] [--by <role>] [--message <file>]`: one line per issue, exit 1 if any. Default: the working tree against HEAD; `--staged`: the index against HEAD (what the commit hook does). A pack file that is absent is not checked (init writes it). In each present file:

- every section exists (`missing section ## X`), every table has its non-computed columns (`missing column(s) …`), enum cells are one of their `values` (lifecycle cells: one of its states), ids match their `pattern` and are unique;
- row by row against HEAD (rows matched by id): a status change must be a path of listed transitions whose `kinds` match the row's kind (a commit may carry several steps, e.g. draft → scheduled; a new row starts at `initial` or one of its first steps, so a ledger row written at `draft` is fine); a row of a lifecycle table is never removed (`rows: "replace"` tables excepted); a HEAD table without the id column is the conversion to the pack (an old ledger reshaped, E34-S4): its rows are checked for shape and values, not compared or moved, so the conversion commit passes the hook;
- the `checks` whose `at` steps the row's path passed, for its `platforms` and `kinds` if listed (social: `disclosure` is for posts and outreach, not replies in our own threads): `link_rule`, `disclosure`, `never_say` (phrases from the brief's Never say list: an item's quoted parts, else the item), `caps` (per platform: posts a day, posts per community per ISO week, replies a day, counting rows in the states from the step's target on), `hold_rules` (a draft going to scheduled that matches a Hold for me rule: a quoted phrase in title/text, or `Field: value`; free-text rules are the Writer's call), `link_present` (going live carries the link).

**Who wrote it.** The writer's role is `--by`, else the `EPICSPINE_PERSONA` env var, else a `Persona: <role>` trailer in `--message`. When known, the validator also checks each transition's `by`, that the role may add rows (`add_rows`) and may write each changed cell (`writers`, field over section) or text section. When unknown, it checks transition legality only, not who. A value that names no pack role is itself an issue. The commit hook (pre-commit) cannot see the commit message, so a wake or the console's write API sets `EPICSPINE_PERSONA=<role>` for its commits (`Jordi` for console writes).

**Commit hook.** `pre_commit.py` runs `pack_validate.staged()`: in a repo whose AGENTS.md turns a pack on, staged pack files with issues block the commit, one `epicspine: pack social: <file> [## section] [<id>]: <issue>` line each; a repo with no pack is not touched; a validator crash is reported and never blocks. Bypass once with `git commit --no-verify`.

## Desk intake (what Jordi says in the desk chat, and where it lands)

A pack's `intake` sorts each desk-chat message into one kind and says where it lands, so the desk files it without guessing and tells Jordi where. `python3 scripts/pack.py social --wake-text` (code: `scripts/pack_intake.py`, `wake_text(schema)`) prints the rule as Markdown; a console pastes it into the desk persona's prompt for a repo that has the pack on (agent_team EPIC-18 Team desk and EPIC-19 repo desk, E34-S10).

- `intake.doc`, `intake.unsure` (what to do when the kind is unclear: ask one line back, never write a guess), `intake.reply` (what every reply names).
- `intake.external.<key>`: a target outside the pack's files (social: `spine`, a new child epic), with `doc`, `path`, `writers`.
- `intake.kinds.<kind>` (in order): `label`, `recognise` (how to tell it), `example`, `targets` (sections `file.section`, fields `file.section.field`, or external keys), optional `set` (field values the write sets, e.g. `ideas.rows.from = Jordi`), `writer` (the role the write commits as), `acts` (who acts on it next), `screen` (where Jordi sees it), `reply` (template; `{link}` is required: the file + `#anchor`, a table row `#L<n>`).
- `check` proves: every target resolves; the writer may write it (a section's `writers`/`add_rows`, a field's writers, an external's `writers`); `set` fields sit in a target and take allowed values; every reply has `{link}`.

The social pack's six kinds:

| Kind | Recognise it | Lands in | Written as | Reply names |
|---|---|---|---|---|
| Brief change (`brief`) | changes the standing campaign (objective, targets, audience, voice, style rule, never say, topic weights, formats, examples, hold rules) | root spine `## Goal` / `## Targets`, message house sections, `data/brief.md` sections | Jordi | the section + line changed, link to the Brief |
| Key message (`key_message`) | push / soften / drop a message across posts | message house `## Points to emphasize` (+ weight) | Jordi | `#6 weight → over`, carried-by on the Brief |
| Priority (`priority`) | this week's or month's highlight, or a do / don't for this week | `data/directions.md` `## Week`, `## Month`, `## This week only` | Jordi | the new H / M line, the Writer's next wake |
| Idea (`idea`) | one post's worth: a topic, angle, link or screenshot | `data/ideas.md` row (`from: Jordi`, `state: new`), a file in `data/assets.md` | Jordi | `I-xx`, the Writer's next wake |
| Big idea → epic (`big_idea`) | more than one post can carry (a tool, persona, video, a series) | a new child epic under the root spine | Delivery manager | the epic code + what it waits on, Home's blocked card |
| Feedback on a post (`feedback`) | a verdict on an existing post | the post row's `Feedback` + message house `## Feedback log` | Jordi | the post id, logged; a repeat becomes a Style rule (C6) |

## JSON export (the console's one typed source)

`python3 scripts/pack.py social --json [--repo <path>]` (code: `scripts/pack_export.py`, `export(name, repo)`) prints ONE JSON document; agent_team's console (E34-S5) codes against this shape. It never crashes on bad data: whatever it cannot read is a `warnings` entry and an empty value.

- Top level, in this order: `schemaVersion` (this export contract, `1`; bumped on a breaking change), `pack`, `packVersion` (the schema's `version`), `repo` (absolute path), `generatedAt` (UTC, `YYYY-MM-DDTHH:MM:SSZ`), `warnings`, then one key per schema file in schema order (social: `brief`, `directions`, `topics`, `ideas`, `posts`, `assets`, `reports`), then `sources`.
- A file with sections is an object keyed by section (`brief.objective`, `directions.week`); a file whose only section is `rows` is that array (`topics`, `ideas`, `posts`, `assets`); a `many` file is an array of `{date, path, <section>: …}` (`reports`, by file name, oldest first). Each section is read where it lives (its own `path`, else the file's) under its `## ` heading (any level; ends at the next heading of that level or higher; `heading: null` = the file's first table).
- Section values by shape: `text` → string (trimmed body) or `null`; `list` → array of item strings (`-`, `*`, `1.` bullets; indented lines join the item); `table` → array of row objects.
- A row: one key per schema field (field names, not column headers; columns matched by exact header, any order) plus `_line` (1-based line in its file, for the write API). Empty, `-`, `—`, `none`, `n/a` cells are `null`. By type: `number`/`percent` → number (leading number read, `40%` → 40); `bool` → `true`/`false`; `url` → the first URL in the cell (a markdown link gives its target); `enum` → lower-cased string; `ref` → one id or `null`; `refs` → array of ids (split on `,` `;` `·` spaces), `[]` when empty; `id`, `text`, `date`, `datetime`, `month`, `role`, `path` → string as written; `\|` in a cell is a literal `|`.
- Computed fields (`computed: {from: "posts.rows.<f>"}`) are arrays of the ids of the rows whose `<f>` names this row: `brief.key_messages[].carried_by`, `directions.week|month[].served_by`, `topics[].used_by`, `ideas[].became`, `assets[].used_by`. A column the file keeps for them is ignored.
- `warnings`: `[{file, line, message}]` (`line` is `null` for a whole file or section). Raised for: no `Pack: <name>` line in AGENTS.md; a file missing (`file missing`; tables and lists `[]`, text `null`); a `many` pattern with no files (`no files`); a section heading not found; a section with no table; missing or unknown columns (one per table); a row with more cells than headers (`row skipped`, it is not exported); a cell that does not fit its type (`not a number`, `not yes/no`, `no URL`, an enum value not allowed, an id off its `pattern`, a date not `YYYY-MM-DD`; the value is kept as written, except numbers and bools, which become `null`); a `ref`/`refs` id not found in its target (not for `rows: "replace"` targets such as topics, whose old ids go by design).
- `sources`: `{"<file>.<section>": {path, heading, exists}}` for every non-`many` section: where the write API (E34-S6) saves it.

Example (trimmed from `tests/fixtures/pack_social.golden.json`, the golden the tests compare against):

```json
{
  "schemaVersion": 1, "pack": "social", "packVersion": 1, "repo": "/home/me/acme-social", "generatedAt": "2026-10-27T12:00:00Z",
  "warnings": [{"file": "data/posts-ledger.md", "line": 8, "message": "row skipped: 24 cells under 22 columns (unescaped |?)"}],
  "brief": {"objective": "Acme becomes a known voice in note-taking: 500 followers by December.", "voice": ["First person singular on Reddit."],
            "key_messages": [{"id": "1", "message": "Your notes are plain files you own", "weight": "over", "source": "Positioning", "carried_by": ["P-0001", "P-0002"], "_line": 7}], "…": "…"},
  "directions": {"week": [{"id": "H1", "highlight": "Launch of sync", "why": "the release", "until": "2026-11-02", "served_by": ["P-0001", "P-0003"], "_line": 7}], "do_dont": [], "voice_note": "Calmer this week.", "month": []},
  "topics": [{"rank": 1, "id": "T-1026-1", "topic": "Files vs databases for notes", "where": "r/notes", "link": "https://reddit.com/r/notes/1", "heat": 8, "date": "2026-10-26", "reply_target": true, "used_by": ["P-0001"], "_line": 5}],
  "ideas": [{"id": "I-1", "date": "2026-10-24", "idea": "Diagram of the commit flow", "format": "diagram", "platform": "X", "from": "Jordi", "link": "A-1", "state": "drafted", "why": null, "became": ["P-0001"], "_line": 5}],
  "posts": [{"id": "P-0001", "date": "2026-10-25", "persona": "Writer", "kind": "post", "platform": "X", "community": null, "slot": "2026-10-25 10:00", "title": "Commit flow",
             "text": "Every change is a commit | see the diagram", "format": "diagram", "assets": ["A-1"], "topic": "T-1026-1", "highlight": "H1", "messages": ["1", "2"], "idea": "I-1",
             "checks": "ok", "link": "https://x.com/acme/status/10", "replies": 3, "metrics": "1.2k views", "result": "good", "feedback": "more like this", "status": "measured", "_line": 5}],
  "assets": [{"id": "A-1", "kind": "diagram", "file": "data/assets/commit-flow.png", "made_by": "Jordi", "source": "drawn", "cuts": "X 16:9", "used_by": ["P-0001", "P-0003"], "_line": 5}],
  "reports": [{"date": "2026-10-26", "path": "data/reports/2026-10-26.md", "numbers": "3 posts, 12 replies.", "best_worst": null, "learned": "Diagrams beat text.", "highlights": null, "feedback": null, "cost": null}],
  "sources": {"brief.objective": {"path": "docs/spines/root.md", "heading": "Goal", "exists": true}, "posts.rows": {"path": "data/posts-ledger.md", "heading": null, "exists": true}, "…": "…"}
}
```

Adding a field to the schema adds a key to its rows (non-breaking); renaming or removing one, or changing a value's type, bumps `schemaVersion`. Tests: `tests/test_pack_export.py` (golden, missing files, computed fields, and a read-only real-shape run over `zenod-social` when a checkout exists).
