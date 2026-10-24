# Human asks: contract (v5)

Page of [EPIC-4](../EPIC-4-DOCTRINE-2.md). v1 was step 12 (agent_team M2-SKILL). v2 is step 17 (M2-SKILL2, Jordi, 2026-10-21). v3 is step 20 ([D19](decisions.md#d19), agent_team M2-35, 2026-10-22): reference lines, search before asking, consumed answers. v4 is D19's amendment (EPIC-0 ticket-34, 2026-10-23): `superseded` asks, done notes, `Waiting on:` code references, advisories on unreadable lines. v5 (EPIC-0 ticket-36, agent_team EPIC-8 E8-S4, 2026-10-24): ask-writing rules and their advisories. Earlier shapes are unchanged.

An ask is a human action that blocks the NEXT step. A human named on a later step is a plan, not an ask: leave it as plain ledger text until that row is next.

An action inside an active standing approval (`## Standing approvals`, own or a parent spine's) is not an ask: do it and cite `under <code>` in Decisions ([standing-approvals.md](standing-approvals.md)). At kickoff, propose the grants the build will need as one `approve` ask.

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

**Write it so the human answers in seconds** (whoever raises it, the delivery manager first; agent_team root L-13, L-14):
- **Only the step that blocks now.** A human step later in the plan (a QR scan "when pinged", keys "before Wave 2") stays plain plan text and becomes an ask only when it is next. Asks ahead of time blur what is really blocking.
- **Lead with the decision in plain words:** what, why it matters, the recommendation. Ids, jargon and steps come after, in the fields.
- **One decision per ask.** Never fold non-blocking extras into a blocking ask: a key, a token widening, a redirect and a future scan are four asks at most, and only the one blocking now is written (whatgpt_v3 E0-A7 folded all four).
- An agent that answers asks for the human (an Unblocker) answers or splits them; it never rewrites an ask's wording. Phrasing is the asker's job.

**Then the fields, each introduced by ` — `:**

| Field | Required for | What it holds |
|---|---|---|
| `steps:` | `do` | the exact commands, or a link to a runbook that has them, plus the host and user |
| `options: A \| B` | `decide` | the choices |
| `recommend:` | `decide`, `approve`, `do` | a concrete choice or action, never "your call" |
| `unblocks:` | all | which rows proceed once answered, and the cost of waiting |
| `effort:` | optional | e.g. `~10 min` |
| `context:` | all | a page or anchor with the background |

**Row status word:** the blocked row is set to `blocked`. Current State's `Waiting on:` lists the codes, e.g. `Jordi: E4-A3, E4-A4` (any ask code it names, this epic's or another's, `<repo>/<code>` across repos, is read as a reference); `nobody` or `none` (first word) means no human blocks, whatever follows.

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

**Superseded:** an ask replaced by another before it was answered becomes `- [superseded <code> <YYYY-MM-DD> by [<repo>/]<code>] <question> …`. It is closed like `done`; the new ask carries the wait.

## Consumed answers
After acting on an `[answered ...]` line, the owner appends ` · done <YYYY-MM-DD> <sha>` to it (the commit that acted on the answer; a short note may follow, and the marker may also sit inside the tag after `@<who>`, with ` superseded by <code>`):

```
- [answered EPIC-4-A1 2026-10-21 @Jordi] Approve the doctrine page? — answer: APPROVED · done 2026-10-22 7efe0ee
```

Tools read it as closed: `state: "done"`, never listed as work, never open, stale or surplus. An `answered` line without `done` is the owner's action item. Deleting the line after its Decisions row exists stays valid.

## Reference, not ask
A spine blocked by an ask that already exists anywhere writes one line instead of a second ask:

```
- [waits on infra-vps/EPIC-10-A7 row 3] The VPS key Jordi is providing
```

- `[waits on <code> row <id>]` plus a one-line gloss. `row` is the row of THIS spine that is blocked. Across repos the code is qualified `<repo>/<code>` (GitHub repo name, not owner/name).
- It has no fields, does not count toward the 3-ask limit, never goes stale, and satisfies the blocked-row check below.
- The canonical ask's `unblocks:` may name rows in other epics as `<repo>/<epic code> row <id>`.
- The line is set to `blocked` like any ask's row; remove it when the target ask is `done` or gone.

## Search before asking
Before raising an ask, check, in this order: the open asks in this repo's tree (`spines.py --json`, each node's `waiting_on`), the same in the other repos the epic touches, and the console's open Needs Jordi items. If one matches, write a reference line (above). A console Needs Jordi item and a spine ask for the same question are ONE ask: the item's question starts with the spine code (`EPIC-4-A2: ...`), never a second code.

**v1 lines** (`[ask: decide @Jordi …]`, no code) still parse: `code` is null and the checks give the advisory warning "ask has no code".

## In `spines.py --json` (per node)
```json
"waiting_on": [{"code": "E4-A3", "who": "Jordi", "ask": "do", "question": "...", "steps": "docs/runbooks/archiver-patch.md#run (vps1, user root)",
  "options": [], "recommend": "do it tonight", "unblocks": "S2, S3; each day waiting loses a day of archived ticks", "effort": "~10 min",
  "context": "docs/one-logger/notes.md#archiver", "since": "2026-10-21", "row": "S3", "state": "open", "answer": null}]
```
Unknown or missing fields are null. On an `answered` or `superseded` line, `code` is kept, and `ask`, `since` and `row` may be null (`who` too when superseded). `state` is `open`, `answered`, `done` (`· done` consumed answer; `answer` excludes the suffix) or `superseded`. `superseded_by` is the code after `by` (`[superseded …]`, or `superseded by` in an answered tag), else null. An ask type outside the four is kept as written (and warned). `waiting_on` never holds reference lines.

Reference lines are a separate per-node list, `[]` when there are none:
```json
"waits_on": [{"ref": "infra-vps/EPIC-10-A7", "repo": "infra-vps", "code": "EPIC-10-A7", "row": "3", "state": "open", "via": "waits_on"},
             {"ref": "E4-A8", "repo": null, "code": "E4-A8", "row": null, "state": "done", "via": "waiting_on"}]
```
- `ref` is the target as written (`<repo>/<code>` or `<code>`); `repo` is the qualifier or null (same repo); `row` is this spine's blocked row, or null.
- `via` is `waits_on` (a `[waits on]` line) or `waiting_on` (a code named in Current State's `Waiting on:`; `row` null). A code appears once, a line first; a code of this node's own ask points at that ask (same code in `waiting_on`). `nobody`/`none` adds nothing.
- `state` is the target ask's state (`open`, `answered`, `done`, `superseded`) when it resolves, else `unresolved`.
- Resolution: a bare code, or one qualified with this repo's own name (folder name or the `Repository:` header), is looked up in this repo's tree (ask lines, else `done` when only a Decisions row cites the code, i.e. its line was cleaned up); any other repo is read from the sibling checkout `../<repo>`, and is `unresolved` when that checkout is absent or has no tree.

## Checks (advisory; they never block a commit)
The validator and the commit check warn on:
- a row or epic that is `blocked` or `waiting` on a human with no open ask naming it;
- a row that is next (status `ready` or `active`) with a human in its Needs/Owner column and no ask;
- an ask missing a required field, or missing its code;
- a duplicate code within an epic;
- a bare internal id in the question (best effort);
- an ask that names a future trigger ("when pinged", "before Wave", "later", "once … is up"): ask only for the step that blocks now (best effort, over the question, `steps:` and `recommend:`);
- a question that lists several numbered parts, "(1) … (2) …": one decision per ask;
- a question sentence over 200 characters: lead with the decision in plain words;
- more than 3 open asks;
- an ask open for more than 7 days;
- a `waits on` or `Waiting on:` code of this repo that no ask or Decisions row cites (a cross-repo one never warns, it reports `unresolved`);
- a `## Waiting on` bullet the tools cannot read, an unknown ask type, or extra text in an `answered` tag, naming the canonical form;
- a Current State `Waiting on:` that names a human (`Jordi: …`, `Jordi — …`) but no ask code (write the codes, or `nobody`).

A `waits on` line satisfies the first checks (a row or epic blocked on it has an ask naming it). `done` and `superseded` lines are not open asks, so the open-count, stale and missing-field checks skip them.

Under `--trackable`, these are reported as issues.
