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
| `pack.py <name> --json` | exports the repo's typed data for the console, with computed back-links | E34-S3 |

## Opt in

One line in the repo's `AGENTS.md` (repo values, outside the EpicSpine block): `Pack: social`. Several: `Pack: social, sales`. `EpicSpine packs: social` is read the same way. `python3 scripts/pack.py list --repo <path>` prints the packs a repo has on; without `--repo` it lists the packs the skill ships.

## Schema shape (`schema.json`)

- `pack`, `version`, `opt_in`, `owner` (the human role), `approval_gate` (`false`: the lifecycle `path` never waits on the owner), `roles` (role name → remit, one line).
- `files.<file>`: `path` (repo-relative; `{date}` + `many: true` for one file per item), optional `dir` (binary files), `sections`.
- `sections.<section>`: `heading` (the `## ` heading; `null` = the file's one table), optional `path` (a section kept in another file, e.g. the root spine's `## Goal`), `shape` (`text` | `list` | `table`), `writers` (roles; default for its fields), `add_rows` (roles that may add a row), `rows: "replace"` (the writer replaces the table each run), `fields`.
- `fields.<field>`: `column` (exact table header), `type` (`id` with `pattern`, `text`, `number`, `percent`, `bool`, `date`, `datetime`, `month`, `url`, `path`, `enum` with `values`, `role`, `ref`/`refs` with `ref: ["file.section", …]`), optional `writers` (overrides the section's), `computed: {from: "file.section.field"}` (derived by the export, nobody writes it), `lifecycle: <name>` (its values and writers come from that lifecycle).
- `lifecycles.<name>`: `field` (the status field it drives), optional `kind_field`, `initial`, `path` (the normal way through), `states` (state → meaning), `transitions` (`from`, `to`, `by` roles, optional `kinds`, `when`, `effect`). A status change not listed, or made by a role not in its `by`, is illegal.
- `effects` (what a transition does besides the cell), `rules` (cross-file automations, e.g. repeated feedback → a style rule), `checks` (what the validator runs, `at` the `from>to` transitions, with `params`).

Addresses are dotted: `file.section` and `file.section.field` (single-table files use section `rows`).

## Self-consistency

`python3 scripts/pack.py check [<name>]` (exit 1 on errors), used by `tests/test_packs.py`: every role named is in `roles`; every file, text section and non-computed field has a writer; every state is reachable from `initial`; every `path` step is a transition that some non-owner role can make when `approval_gate` is false; refs, `computed.from`, `kind_field`, effects, rules and check sources resolve. Add a pack by adding `packs/<name>/schema.json` and running `check`.

## Init

`python3 scripts/pack.py init social --repo <path>` writes each missing pack file from its sections' `heading` (`## …`) and the `column`s of their fields (heading `null` = the file's one table; `computed` columns are left out, the export derives them). It never overwrites: a file that exists only gains the sections it lacks, appended at its end; a missing spine (`docs/spines/…`, e.g. the brief's Goal/Targets in the root spine) is never created, only noted, and once it exists a rerun appends its missing headings; a file's `dir` gets a `.gitkeep`; per-item files (`many`, reports) are written by their persona. It adds `Pack: social` to AGENTS.md (creating it if needed) when absent. Idempotent: a second run prints `nothing to do`.

## Validate

`python3 scripts/pack.py validate [--repo <path>] [--staged] [--by <role>] [--message <file>]`: one line per issue, exit 1 if any. Default: the working tree against HEAD; `--staged`: the index against HEAD (what the commit hook does). A pack file that is absent is not checked (init writes it). In each present file:

- every section exists (`missing section ## X`), every table has its non-computed columns (`missing column(s) …`), enum cells are one of their `values` (lifecycle cells: one of its states), ids match their `pattern` and are unique;
- row by row against HEAD (rows matched by id): a status change must be a path of listed transitions whose `kinds` match the row's kind (a commit may carry several steps, e.g. draft → scheduled; a new row starts at `initial` or one of its first steps, so a ledger row written at `draft` is fine); a row of a lifecycle table is never removed (`rows: "replace"` tables excepted);
- the `checks` whose `at` steps the row's path passed, for its `platforms` if listed: `link_rule`, `disclosure`, `never_say` (phrases from the brief's Never say list: an item's quoted parts, else the item), `caps` (per platform: posts a day, posts per community per ISO week, replies a day, counting rows in the states from the step's target on), `hold_rules` (a draft going to scheduled that matches a Hold for me rule: a quoted phrase in title/text, or `Field: value`; free-text rules are the Writer's call), `link_present` (going live carries the link).

**Who wrote it.** The writer's role is `--by`, else the `EPICSPINE_PERSONA` env var, else a `Persona: <role>` trailer in `--message`. When known, the validator also checks each transition's `by`, that the role may add rows (`add_rows`) and may write each changed cell (`writers`, field over section) or text section. When unknown, it checks transition legality only, not who. A value that names no pack role is itself an issue. The commit hook (pre-commit) cannot see the commit message, so a wake or the console's write API sets `EPICSPINE_PERSONA=<role>` for its commits (`Jordi` for console writes).

**Commit hook.** `pre_commit.py` runs `pack_validate.staged()`: in a repo whose AGENTS.md turns a pack on, staged pack files with issues block the commit, one `epicspine: pack social: <file> [## section] [<id>]: <issue>` line each; a repo with no pack is not touched; a validator crash is reported and never blocks. Bypass once with `git commit --no-verify`.
