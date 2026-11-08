# Machine Dispatcher

Env `EPICSPINE_DISPATCHER` is a command line (shlex-split). The manager runs it directly and reads its JSON; each call prints one object and exits 0. Adapters live outside the skill (`examples/dispatchers/`).

| Call | Output |
|---|---|
| `status` | `{"name": "seat pool", "capacity": 2, "available": 1}` |
| `pick [--task TEXT]` | `{"id": "seat1", "via": "t3_delegate_task", "providerInstanceId": "...", "model"?: "..."}` |
| `pick`, none free | `{"id": null, "reason": "...", "retryable"?: true, "retry_after_s"?: 60}` |
| `done <id> [--fail] [--signal TEXT]` | `{"ok": true}` |

The only `via` is `t3_delegate_task`: call T3 MCP `delegate_task` with `target.providerInstanceId` (and `model`). Unknown `via`, missing field, non-zero exit, or non-JSON is a failure.

Flow: check the env and run `status` at thread start, every thread, greetings included (never assume unset or recall a value); name = `status.name` verbatim; per worker `pick`, dispatch (the worker still makes its own worktree), `done <id>` when finished, `done <id> --fail --signal "<error text>"` so the dispatcher can mark a limit. `id: null` (never implement the work yourself):
- Never launch the worker on another host or hand it to a console instead (agent_team E6-S63: workers run on VPS3 only; an old `fallback` field is ignored).
- `retryable` true (or absent): pick again in this same turn after `retry_after_s` (default 60), doubling the wait, about 15 min in total; wait with a Monitor or until-loop, never a foreground sleep.
- still refused at the end, or `retryable: false`: record the rows as queued with the reason and end the run with `retryAt` about now + 10 min. Never write "the next scheduled wake dispatches it".

Failure: say so in the reply and use a native subagent.

Precedence: per-task user instruction > repo `Dispatch profile: local-only` (machine dispatcher ignored) > machine dispatcher (where) > repo `Dispatch profile:` > `~/.agents/epicspine-profile.md` > lower-cost native subagent.

Bind suffix: `Delivery manager · EpicSpine · Learnings in force: <ids> · dispatch: <status.name> (<status.available>/<status.capacity> seats)`; on failure `· dispatch: unavailable → native subagent`.
