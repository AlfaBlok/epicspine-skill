# Human asks: contract (v2)

Page of [EPIC-4](../EPIC-4-DOCTRINE-2.md). v1 was step 12 (agent_team M2-SKILL). v2 is step 17 (M2-SKILL2, Jordi, 2026-10-21). The console may code against v2 now.

An ask is a human action that blocks the NEXT step. A human named on a later step is a plan, not an ask: leave it as plain ledger text until that row is next.

## Writing an ask
Write one line per ask under `## Waiting on`, right after Current State.

```
## Waiting on
- [ask E4-A3: do @Jordi since 2026-10-21 row S3] Patch the archiver for 1 h on vps1 so the Chainlink cutover can run — steps: [runbook](docs/runbooks/archiver-patch.md#run) (vps1, user root) — unblocks: S2, S3; each day waiting loses a day of archived ticks — recommend: do it tonight — effort: ~10 min — context: [why](docs/one-logger/notes.md#archiver)
```

**Tag:** `[ask <code>: <type> @<who> since <YYYY-MM-DD> row <id>]`
- `code` is `<epic code>-A<n>`.
  - The epic code comes from the title: `EPIC-4`, or a legacy short id such as `E4` or `M2`.
  - `n` counts up per epic and is never reused: take the highest A-number in Waiting on and Decisions, plus 1.
  - Inside a repo, the code alone is unambiguous. Across repos, qualify it as `<repo>/<code>`, e.g. `poly-maker/E4-A3`.
- `type` is one of:
  - `decide`: choose between options;
  - `approve`: yes or no on a proposal;
  - `provide`: give a value, secret or file;
  - `do`: the human must act themselves (root, a login, a physical step).
- `who` is the named human. `since` is the date the ask was first written.
- `row` is optional: the ledger step this ask blocks.

**Then:** the question, as one self-contained sentence. Every internal id in it gets a gloss: "S3 (patch the archiver)", never a bare "S3".

**Then the fields, each introduced by ` — `:**

| Field | Required for | What it holds |
|---|---|---|
| `steps:` | `do` | the exact commands, or a link to a runbook that has them, plus the host and user |
| `options: A \| B` | `decide` | the choices |
| `recommend:` | `decide`, `approve`, `do` | a concrete choice or action, never "your call" |
| `unblocks:` | all | which rows proceed once answered, and the cost of waiting |
| `effort:` | optional | e.g. `~10 min` |
| `context:` | all | a page or anchor with the background |

**Status:** the blocked row gets Status `blocked`. Current State's `Waiting on:` lists the codes, e.g. `Jordi: E4-A3, E4-A4`.

## Keep it minimal (the manager's duty)
On every wake and at every session end, the delivery manager rewrites `## Waiting on` as the smallest set of human actions:
- Merge asks that one human action resolves.
- Order them by the critical path.
- Aim for at most 3 open asks per epic.
- Make each ask answerable in 5 minutes or less, without opening a file.
- Keep `recommend:` concrete.
- Close or drop any ask that no longer blocks.
- Never write an ask for a future gate.

## Answering it
1. **An answer that cites a code applies to that ask,** on any channel (console, chat, voice): for example "E4-A3: done" or "EPIC-4-A1: approved".
2. **Delivery:** the console delivers the answer to the owner's thread. That is the attached persona's thread, else the `thread <id>` in Current State's `Owner:` (`current_state.owner`).
3. **Write-back:** the owner rewrites the line as `[answered <code> <YYYY-MM-DD> @<who>] … — answer: <answer>`, adds a Decisions row that cites the code, and unblocks the row.
4. **Cleanup:** once the Decisions row exists, the answered line may be deleted. A code is never reused.

So an `ask` line is open, an `answered` line is answered but not yet cleaned up, and no line means nothing is pending.

**v1 lines** (`[ask: decide @Jordi …]`, no code) still parse: `code` is null and the checks give the advisory warning "ask has no code".

## In `spines.py --json` (per node)
```json
"waiting_on": [{"code": "E4-A3", "who": "Jordi", "ask": "do", "question": "...", "steps": "docs/runbooks/archiver-patch.md#run (vps1, user root)",
  "options": [], "recommend": "do it tonight", "unblocks": "S2, S3; each day waiting loses a day of archived ticks", "effort": "~10 min",
  "context": "docs/one-logger/notes.md#archiver", "since": "2026-10-21", "row": "S3", "state": "open", "answer": null}]
```
Unknown or missing fields are null. On an `answered` line, `code` is kept, and `ask`, `since` and `row` may be null.

## Checks (advisory; they never block a commit)
The validator and the commit check warn on:
- a row or epic that is `blocked` or `waiting` on a human with no open ask naming it;
- a row that is next (status `ready` or `active`) with a human in its Needs/Owner column and no ask;
- an ask missing a required field, or missing its code;
- a duplicate code within an epic;
- a bare internal id in the question (best effort);
- more than 3 open asks;
- an ask open for more than 7 days.

Under `--trackable`, these are reported as issues.
