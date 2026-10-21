# Spine Model

Conceptual model: hierarchy, artifact authority, profiles, and write scope.

## Connected Spine Model

Treat every EpicSpine as a node in a canonical ownership hierarchy:

- Prefer one canonical root spine per repository or coherent project. Multiple roots are allowed only when they represent intentionally independent ambitions; record why each additional root cannot be a branch of the canonical root.
- Every non-root spine has exactly one canonical parent and inherits exactly one root. Parentage may nest to any depth.
- The canonical hierarchy is a rooted tree, or an explicitly justified forest when multiple roots exist. Cross-links may form a wider knowledge graph, but they do not change canonical parentage or rollup ownership.
- Every spine declares a stable Spine ID. Connected spines additionally declare Spine Type, Root Spine, and Parent Spine. A parent lists each direct child in its Spine Map; a child links back to its parent and root.
- A child owns its local mission, acceptance, execution state, backlog, decisions, and evidence. Its parent owns only the compact rollup, dependencies, health, and cross-child decisions.
- Roll up direct children one level at a time. Do not copy descendant issue ledgers or deep history into ancestors.

`AGENTS.md`, repository instructions, and launch prompts may route a cold start to the root spine. They must not duplicate live project state. The root spine is the canonical starting point; agents follow its active-branch links until reaching the spine bound to their work.

## Epic Log

Wording: the root spine is the trunk; a goal (epic) is a node; the **epic log** is the one tree per repo. Files and header fields keep their names.

- A goal hangs from the root spine (which states the repo's purpose) or from another goal. Spines are nested markdowns: progress within a goal is written in that goal's spine. A new measurable objective worked over iterative pushes (a sprint or plan, each push unblocking the next) gets a new leaf markdown linked from its parent; a small one-push item stays a `- [ ] <ID> text` line in its parent's Definition Of Done. Judgment, not a hard rule.
- Every goal is named `EPIC-<n>: <short name>` (file title `# EPIC-<n>: <name>`), states its goal in one line and lists measurable success criteria; without a code it cannot be discussed.
- The child's `Parent spine:` header is the structural authority; the parent's Spine Map must list it with the same Spine ID. A disagreement (either way, or a row pointing at a missing file) is a mismatch. Parent state rolls up from children (blocked wins; all children and criteria done = done; any progress = active).
- Goal doc = a file with a `Spine ID:` line or named `E<n>-*`, `EPIC*`, `*SPINE*`, `*PLAN*` (not under `archive/`, `node_modules`, dot-dirs, `handoffs/`, `examples/`, `fixtures/`, `test/`, `tests/`, or a vendored skill). One not in the tree is an orphan. Header and Spine Map links resolve against the file's own folder, else the repo root (`Parent spine: docs/spines/root.md` works from any folder).
- Create with `spine_new.py` (`references/spine-creation.md`); `pre_commit.py` blocks a newly added/renamed goal doc, or a modified one whose HEAD version already had `Spine ID:`, that has no valid header, is not reachable from the root, or disagrees with its parent's map (`--trackable` + tree only; `--strict` stays advisory). It only warns for a modified legacy doc (no `Spine ID:` at HEAD: migrate it with `spines.py`/`spine_new.py`), a root spine with no `Spine ID:` header (migrate the root first), and `Root spine: none`.
- `spines.py --json --repo DIR` is the discovery contract (console pickers consume it; always exit 0):

```
{"root": "<path>" | null,
 "nodes": [{"id", "path", "title", "type", "parent": "<path>" | null, "status", "rollup_status",
            "dod": [{"id", "text", "done"}], "outcome": {...} | null, "current_state": {...} | null, "children": ["<path>", ...]}],   # depth-first from the root; paths are repo-relative
 "orphans": [{"path", "title", "reason"}],      # goal docs outside the tree
 "mismatches": [{"path", "parent", "problem"}]} # header/map disagreement, missing map target
```

## Spine Versus Issues

Declare `Ticket backend: github|local` (omission defaults to github). GitHub mode retains the existing offline URL/status checks and clearly unverified ledger snapshots. Local mode declares `Ticket root`, uses a reference/dependency-only Issue Ledger, and puts Ticket ID, Status, Owner and Evidence in each authoritative ticket file. Never maintain both a mutable local ticket and copied status cells in its spine. Read `references/ticket-backends.md` for path boundaries, normalized records and verification semantics. No backend choice implies remote access, record migration or new read authority.

- The spine explains why the work exists, what outcome is desired, how the pieces fit together, what the current state is, and where a new agent should go next.
- GitHub issues explain the detailed work for one concrete step: code paths, blockers, implementation notes, logs, review comments, and ticket-level validation.
- Keep the spine clean. Prefer compact state, decisions, links, and evidence over long debugging transcripts or code-level detail.
- Put deep ticket discussion in the GitHub issue or PR, then summarize only the durable consequence back into the spine.
- If an issue discussion changes intent, scope, acceptance, dependency, or current state, write that change back into the bound spine.

## Machine-Read Contract

Dashboards and tools read only these; keep them exact, and write everything else for humans:

- `## Definition Of Done` (tickets: `## Acceptance`/`## Acceptance Criteria`): every criterion is `- [ ] <ID> <criterion>` or `- [x] <ID> ...` plus an optional short evidence note. ID `[A-Z][A-Z0-9]*-\d+` (M4-1, X-1), unique in the file, never renumbered; indented lines continue an item, prose and tier labels (`SHIP —`) are not criteria. Say how a measurable criterion is measured (metric, threshold, window, command).
- `## Current State`: `Status:` is the only status source; `Waiting on:` is context and never implies blocked. Consumers (console badges) read `Status:` only; `spines.py --json` also carries its labels as `current_state`. The manager refreshes Last attempted, Result, Waiting on, Next action and Verified at at the end of every working session or wake, not only at milestones.
- `## Waiting on`: the smallest set of human asks (≤3, only what blocks the NEXT step), one line each: `- [ask <epic>-A<n>: decide|approve|provide|do @<who> since <date> row <id>] <question> — steps: … (do) — options: A | B (decide) — recommend: X — unblocks: <rows, cost of waiting> — effort: ~5 min — context: <link>`; the blocked row gets Status `blocked`, Current State's `Waiting on:` lists the codes. An answer citing a code applies to that ask: rewrite the tag to `[answered <code> <date> @<who>]`, append ` — answer: X`, add a Decisions row, unblock. `spines.py --json` carries `waiting_on`; contract <https://github.com/AlfaBlok/epicspine-skill/blob/main/docs/doctrine/human-asks.md>; incomplete, duplicate, stale or surplus asks only warn.
- `## Issue Ledger`: the table with columns Issue, Title, Owner (`Owner / Assignment` is fine) and Status; Status is one of draft / ready / active / blocked / done / deferred: `ready` = defined, not started (launching a persona on the spine, e.g. from the agent_team console, is the start order and makes it `active`; the persona carries the goal to completion); `deferred` = paused by the user (`spine_fix` maps on hold/paused/parked to it); `blocked` = waiting on a named external dependency. A local-backend ledger is reference-only and carries no Status.
- Other work tables are not read.

Enforcement is `validate_spine.py --trackable` (valid Status, criteria as above, a ledger Status column — or valid ticket-file Status for local), run by the repo's pre-commit hook, which the SessionStart hook installs in EpicSpine repos. The commit fixes what it can without guessing (`validate_spine.py --fix`: criteria to `- [ ] <ID> ...`, alias headings such as `## Exit Test` to `## Definition Of Done`, status synonyms such as in progress to active) and blocks only on a missing Status, Status column or criterion; `--strict` stays advisory there. `validate_spine.py` also warns when Definition Of Done has no checkbox; a github ledger without Status already fails (`references/structural-validation.md`).

## Outcome

Every spine gets `## Outcome` written when its goal closes (done, abandoned or superseded). It holds the verdict, one sentence, each Done means item mapped to evidence links, residual risk/follow-ups, and date plus closing agent/run. `Status: done` (or a `Superseded by:` close) is invalid without a filled Outcome; `--trackable` blocks it, and `--fix` never invents one. The parent's rollup cites the child's outcome sentence. `spines.py --json` carries it per node as `outcome` (`null` when absent; shape in `docs/doctrine/console-contract.md`).

```
## Outcome
Verdict: accomplished | partially accomplished | not accomplished | superseded
Outcome: <one sentence>
Closed: <YYYY-MM-DD> by <agent / run>
Risk: <text or none>
| Done means | Evidence |
|---|---|
| <ID and text> | [PR #31](https://github.com/o/r/pull/31), 0891cbb |
```

## Authority By Artifact

Do not treat one artifact as authoritative for every kind of truth:

- The EpicSpine is authoritative for intent, scope, epic acceptance, dependencies, decisions, and rollup state.
- The declared backend record (GitHub issue or local ticket file) is authoritative for detailed execution state of one ticket; offline GitHub ledger values remain unverified snapshots.
- The branch, pull request, and code are authoritative for the implementation that actually exists.
- Validation evidence is authoritative for what has been proved in a named environment against a named commit.
- The Epic 0 spine is authoritative for project direction, child-spine relationships, and cross-epic health.

When a repository declares an active Book companion:

- The Book is authoritative for the navigable, user-facing body of accumulated knowledge and synthesis.
- When present, its canonical registry is authoritative for the current structured collection or shortlist rendered by the Book.
- Chapters organize domains and index their leaves; leaves own the substantive explanation, research, comparison, or conclusion for one bounded question.
- Evidence remains authoritative for the underlying claims. A polished Book leaf does not outrank current code, data, source documents, or validation.

The active spine steward reconciles contradictions. Never overwrite observable code or test evidence merely because the spine says something older.

## Write Scope

Default rule: **read broadly, write narrowly.**

- The agent's **bound spine** is the primary spine named by the user, issue, branch, or explicit task context. It is the only spine the agent may edit by default.
- Each spine must name one **active steward**. The Epic 0 worker normally stewards the root spine; the epic worker normally stewards a child spine; a planner may steward a spine during planning when explicitly bound.
- The steward reconciles and commits spine updates. Other agents write detailed state to their bound issue and submit a structured handoff unless explicitly delegated a narrow spine section.
- Do not let multiple agents concurrently rewrite mission, acceptance, current state, or the issue ledger. Transfer stewardship explicitly when the active writer changes.
- Referenced parent, child, sibling, portfolio, roadmap, or meta-spines are read-only context unless the user explicitly says the agent may edit that spine.
- If the agent notices drift in a read-only spine, record a proposed cross-spine update in the bound spine's Open Questions, Planner Queue, or Handoff Journal. Include the target spine, proposed change, evidence, and suggested owner.
- Do not update another spine just because the current work affects it. Create a GitHub issue, handoff note, or proposed update for that spine's planner.
- If a task genuinely requires editing multiple spines, state the requested write set before editing and keep each edit scoped to that spine's authority.

Use parent or portfolio spines for rollups, dependencies, health, and cross-epic decisions. Keep child spines authoritative for their own implementation state, validation evidence, and ticket ledger.

Normal rollup does not grant a parent steward authority to rewrite child detail. The child steward publishes the rollup or sends a structured proposal; the parent steward reconciles the parent row.

## Active Profile And State

Use `assets/compact-spine-template.md` for a small active epic. Declare `Spine profile: compact`; keep one authoritative `Current State` with owner, status, last action/result/evidence, one waiting/blocker condition, approved work, exact next action, and verified source revision/time. Phase is optional context. Do not author another cursor, role queue or handoff summary containing competing current facts; use links or explicitly generated projections.

The compact profile requires Mission, Non-Goals, Current State, Definition Of Done, Issue Ledger and Decisions. Add hierarchy, recovery, write-scope gates and Book details when applicable. Stable ID, repository, document path and integration branch remain required. A standalone compact spine makes no hierarchy claim; `--graph` requires explicit lineage fields before it can validate connection.

Absent `Spine profile` or `Spine profile: full` retains legacy requirements. Legacy Current State/Execution Cursor documents remain readable; contradictory aliases produce source-located conflicts, never an inferred winner. Reconcile meaning as the steward before migration. Keep completed handoffs in linked history while preserving rejected decisions, evidence, IDs and old fragments. See `references/compact-state.md` for the normalized state API, conservative migration preview and history rules.

Profile and dialect are separate: compact v1 is a small structural contract; opt into v2 for its SHIP/HARDEN acceptance. The full template remains available for existing v1/v2 workflows and explicit legacy compatibility.

## Name

Call the pattern **EpicSpine** in conversation. Use `epic-spine` for files, labels, branches, and skill references when a machine-friendly name is needed.

