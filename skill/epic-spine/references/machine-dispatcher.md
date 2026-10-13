# Machine Dispatcher

Read this when env `EPICSPINE_DISPATCHER` is set, or when writing a dispatcher. One machine-level hook decides where workers run in every repo, so no repo needs a dispatch rule. Core defines only the contract; adapters live outside the skill (`examples/dispatchers/`).

## Contract

`EPICSPINE_DISPATCHER` is a command line (shlex-split; may be `python3 /path/x.py`). Each subcommand prints one JSON object on stdout and exits 0.

| Call | Success output |
|---|---|
| `status` (read-only) | `{"name": "seat pool", "capacity": 2, "available": 1, ...}` |
| `pick [--task TEXT]` | `{"id": "<reservation>", "via": "<how>", ...via fields}` |
| `pick`, all busy or maxed | `{"id": null, "reason": "..."}` |
| `done <id> [--fail] [--signal TEXT]` | `{"ok": true}` |

| `via` | Fields | Manager action |
|---|---|---|
| `t3_delegate_task` | `providerInstanceId`, optional `model` | T3 MCP `delegate_task` with `target.providerInstanceId` (and `model`) |
| `native_subagent` | optional `model` | the harness's own subagent tool |
| `command` | `argv` (list) | run `argv` with the brief |

Any other `via`, or a missing required field, is a dispatcher failure.

## Manager Flow

1. Thread start: `scripts/dispatcher.py status`.
2. Per worker: `scripts/dispatcher.py pick --task "<one line>"`, dispatch as `via` says (the worker still creates its own worktree), then `scripts/dispatcher.py done <id>` when it finishes; on failure `done <id> --fail --signal "<error text>"` so the dispatcher can mark a limit.
3. `id: null`: queue or wait, then retry. Never fall back silently and never implement the work yourself.
4. Dispatcher failure (command missing, non-zero exit, timeout, non-JSON, unknown `via`): `dispatcher.py` prints `{"error": "..."}` and exits 2. Say so in the reply and use a native subagent.
5. Model and reasoning fields of the repo or machine profile still apply when the `via` accepts a model; the dispatcher's own `model` wins.

`dispatcher.py` reads the env, applies a 20s timeout, validates the contract, and passes JSON through. Unset env prints `{"active": false}`: behaviour is exactly the profile-based default.

## Precedence

Per-task user instruction > repo opt-out `Dispatch profile: local-only` (root spine or `AGENTS.md`; the machine dispatcher is ignored, `dispatcher.py` reports inactive) > machine dispatcher (where) > repo `Dispatch profile:` > `~/.agents/epicspine-profile.md` > lower-cost native subagent.

## Bind Suffix

`dispatcher.py bind` prints the suffix, empty when inactive. Append it to the bind line:

- Active: `Delivery manager · EpicSpine · Learnings in force: <ids> · dispatch: <name> (<capacity> seats)`
- Failed: `... · dispatch: unavailable → native subagent`
