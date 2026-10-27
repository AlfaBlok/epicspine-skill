# Packs: typed vertical files a repo opts into

Base EpicSpine knows goals, state, ledgers, asks, learnings and the Team table; a repo may keep other files (`data/*.md`) but the base never says their shape. A **pack** says it for one vertical: the files, their sections and fields, the item lifecycles (statuses and legal transitions) and which persona role may write what, so personas, the commit-hook validator and the console screens agree on one shape. A pack is not a new spine type; spines stay as they are.

## What a pack is

`packs/<name>/` in the skill:

| File | Holds | Built in |
|---|---|---|
| `schema.json` | the machine-read schema: the one source every tool reads | E34-S1 |
| `README.md` | the human doc: files, statuses, who writes what | E34-S1 |
| `validate.py` (or a `pack.py validate` mode) | checks a repo's files against the schema in the commit hook | E34-S2 |
| `pack init <name>` | creates the files with the right headings and columns | E34-S2 |
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
