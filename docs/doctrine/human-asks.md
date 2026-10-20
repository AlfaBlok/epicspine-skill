# Human asks: contract

Page of [EPIC-4](../EPIC-4-DOCTRINE-2.md), step 12. Requested by agent_team M2-SKILL (Jordi, 2026-10-21). The console may code against it now.

## Writing an ask
An agent that is blocked on a human writes one line per ask under `## Waiting on` in the epic. Put the section right after Current State.

```
## Waiting on
- [ask: decide @Jordi since 2026-10-21 row T4] Ship E4 with one logger or two? — options: one | two — recommend: one — context: [why](docs/one-logger/notes.md#loggers)
```

- **Tag** `[ask: <type> @<who> since <YYYY-MM-DD> row <id>]`:
  - `type` is `decide`, `approve` or `provide`;
  - `who` is the named human;
  - `since` is the date the ask was written;
  - `row` is optional: the ledger step it blocks (the first token of that row's Title or its Issue id).
- **Then:** the question, which is one sentence the human can answer without opening anything.
- **Then these fields, each introduced by ` — `:**
  - `options: A | B` (required for `decide`);
  - `recommend: <option or text>` (required for `decide` and `approve`);
  - `context: <link>` (required: a page or anchor that explains the choice).
- **Status:** the blocked ledger row gets Status `blocked`. If the whole epic waits, `Status: blocked` too. Current State's `Waiting on:` names the human and points here, e.g. `Jordi (2 asks, see Waiting on)`.

## Answering it
1. The console delivers the answer to the owner's thread.
2. The owner changes the tag to `[answered <YYYY-MM-DD> @<who>]` and appends ` — answer: <answer>`.
3. The owner adds a Decisions row for it (date, outcome, the answer, who).
4. The owner unblocks the row, setting its Status to whatever it is now.
5. Once the Decisions row exists, the answered line may be deleted. Decisions is the durable record.

So an `ask:` line is still open; an `answered` line has been answered but not yet cleaned up; no line means nothing is pending.

## In `spines.py --json` (per node)
```json
"waiting_on": [{"who": "Jordi", "ask": "decide", "question": "...", "options": ["one", "two"],
  "recommend": "one", "context": "docs/one-logger/notes.md#loggers", "since": "2026-10-21",
  "row": "T4", "state": "open", "answer": null}]
```
- `state` is `open` or `answered`, and `answer` is null while the ask is open.
- `context` is resolved repo-relative when it is a local link.
- The list is empty when there are no asks.

## Checks (advisory; they never block a commit)
The validator and the commit check warn when:
- a ledger row or an epic is `blocked` and no open ask names it;
- an ask is missing a required field;
- an ask is older than 7 days, flagged as "stale ask".

Under `--trackable`, these are reported as issues.
