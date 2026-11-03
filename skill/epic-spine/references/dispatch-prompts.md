# Bootstrap And Dispatch Prompts

The bootstrap response shape and the paste-ready dispatch prompt shapes.

## Bootstrap Response

When orienting another agent or user, return this shape:

```markdown
Current state: ...
Spine lineage: <root -> ... -> bound spine>
Bound role: ...
Bound spine: ...
Bound issue: ...
Spine steward: ...
Book binding: inactive | <root, chapter/leaf, Book steward, author scope>
Goal: ...
Acceptance target: ...
Read path followed: ...
Active issues: ...
Integration target and base: ...
Human gates: ...
Drift or blockers: ...
Last attempted / result: ...
Waiting on: ...
Approved work: ...
Recommended next action: ...
```

Keep it concise; the spine is the durable record.

## Dispatch Prompt Shape

When spawning or briefing workers, use this shape:

```markdown
Use $epic-spine.
Identity: Epic 0 worker | epic worker | ticket worker | tester | planner | reviewer | observer
Bound epic: <path to the epic file; for a ticket worker, the epic its step belongs to>
Learnings: read the Operating Learnings of the bound epic and every `Parent spine:` ancestor up to the root; list their ids in your bind line (never `none` while any exist), then state Goal, Done means open, Next action and where context lives (four short lines) before acting.
GitHub issue: <URL>
Role: Epic 0 worker | epic worker | ticket worker | tester | planner
Spine steward: <task/thread/agent responsible for reconciling the spine>
Assignment identity: <stable task/thread/agent/owner>
Write scope: write detailed work to the issue; edit the spine only if you are its steward or a narrow section is explicitly delegated. Referenced spines are read-only unless listed.
Book binding: inactive | <Book root; owning chapter/leaf; Book steward; author permissions; registry permissions; validation command>
Branch: wt/<task> (local; no push or PR by default)
Base commit: <SHA>
Integration target: <main or declared branch>
Required reads: <bootstrap map links>
Acceptance criteria: <issue and spine criteria>
Human gates: <named approvals or none>
Handoff: update the issue with branch, commits, validation evidence, blocker, and next action; notify the spine steward to reconcile durable state.
Claim: before any work, claim the row: `python3 <skill dir>/scripts/spines.py --claim <row> --by <run id or thread> --repo <checkout>` (one pushed commit; exit 3 = someone else holds it: stop and report the holder, never work it). Every commit names the row code, which renews the lease (default 2 h); `--release` gives it back if you stop.
Review handoff: a finished outcome goes to `review` with its live link in Latest Evidence and its follow-ups in Next Action: `followups: started <code> (<what it covers>), …; start <title> — <why>; park <title> — <why>; confirm: yes — <why the user must confirm it>` (`followups: none` when there are none; `completes: <Done-means id> | goal | ask` when it finishes one). Findings work lists every finding as started or suggested. A step with nothing for the user to confirm closes `done (no confirm: <why>)` and never goes to `review`.
Card: before the row goes to `review`, write its review card, a repo-local file `docs/cards/<row code>.md` (or wherever the repo's card format, e.g. a `review-cards.md`, puts it) whose front matter holds `row`, `title` (one past-tense sentence, ≤20 words: what was made and what it is for), `goal` (the task's goal, ≤20 words), `delivered` (2-4 lines, `✓` or `✗` with the reason), `evidence` (the live thing or a rendered evidence page, never a code-host page or a dry run), `screenshot` (an image of the evidence, in the repo) and, when they apply, `name`, `after`, `next` (`start: <step>` / `park: <step>`), `completes`; `confirm: yes` in the row's Next Action or the card; the repo's root spine names `Project name:` and the epic `Goal sentence:` (add them if missing). Card text is plain words for a normal human: no `;`, `(`, `/` outside links, no row codes, file paths or the word approve. A row that fails the gate comes back as needs evidence or card needs rewriting, never to the user. A row with nothing for the user to judge writes no card and closes `done (no confirm: <why>)` instead. Details: role-protocols.md "Review cards".
```

For an Epic 0 worker that owns the project picture, use:

```markdown
Use $epic-spine.
Identity: Epic 0 worker
Bound spine: <project Epic 0 spine path or URL>
Goal: keep the full project picture and state, create or update child EpicSpines, bind child workers, and loop until the project has clear next actions or needs human input.
Authority: update the Epic 0 spine, create child spine drafts, create/update GitHub issues for coordination, and dispatch child epic workers; referenced child spines are read-only unless explicitly listed.
Child-spine rule: child epic workers own delivery inside their bound child spine; Epic 0 records rollups, dependencies, decisions, health, and cross-epic state.
```

For an epic worker that will dispatch subagents, use:

```markdown
Use $epic-spine.
Identity: epic worker
Bound spine: <path or URL>
Goal: deliver this epic until it is ready for human test, tester handoff, or blocked by required input.
Authority: create/update GitHub issues within existing scope, dispatch ticket workers, and update the bound spine; do not change acceptance or cross-spine scope without planner/user input.
Steward rule: the epic worker is the active steward for the bound child spine; ticket workers and testers return structured issue handoffs unless explicitly delegated a narrow spine section.
Subagent rule: each ticket worker writes deep detail into its assigned GitHub issue; the epic worker writes only clean state, links, blockers, and durable outcomes into the spine.
Integration rule: every dispatched worker/tester uses a local `wt/<task>` branch and separate worktree, then the delivery manager integrates verified work to `main` under `references/git-doctrine.md` so new agents start from the freshest validated base.
```

