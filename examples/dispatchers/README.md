# Dispatchers

A machine dispatcher is the command in env `EPICSPINE_DISPATCHER`. Core EpicSpine only defines the contract (full text: `skill/epic-spine/references/machine-dispatcher.md`); adapters live here.

Each subcommand prints one JSON object and exits 0:

- `status` -> `{"name": "seat pool", "capacity": 2, "available": 1}`
- `pick [--task TEXT]` -> `{"id": "seat1", "via": "t3_delegate_task", "providerInstanceId": "claudeAgent_seat1"}`, or `{"id": null, "reason": "..."}` when all busy
- `done <id> [--fail] [--signal TEXT]` -> `{"ok": true}`

`via`: `t3_delegate_task` (`providerInstanceId`, optional `model`), `native_subagent` (optional `model`), `command` (`argv` list).

## t3_seat_pool.py

Wraps the agent_team seat broker (default `broker.py` beside it; or `SEAT_POOL_BROKER=/path/broker.py`, or `--broker`). On a VPS running T3 Code with seats `claudeAgent_seat1..N`, set in the service unit:

```
Environment=EPICSPINE_DISPATCHER=python3 /home/t3agent/agent_team_m0/broker/t3_seat_pool.py
```

(the adapter sits next to `broker.py`; otherwise set `SEAT_POOL_BROKER` or pass `--broker`).
