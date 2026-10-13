#!/usr/bin/env python3
"""Reference EpicSpine dispatcher: adapts agent_team's seat broker to the contract.

Broker path: --broker PATH, env SEAT_POOL_BROKER, else broker.py beside this file (its `pick`, `done`, and
`status` output shapes are translated; seat null becomes id null).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys


def broker(path: str, *args: str) -> str:
    return subprocess.run([sys.executable, path, *args], capture_output=True, text=True, check=True, timeout=15).stdout


def main(argv: list[str]) -> int:
    path = os.environ.get("SEAT_POOL_BROKER") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "broker.py")
    if argv[:1] == ["--broker"]:
        path, argv = argv[1], argv[2:]
    if not argv:
        print("usage: t3_seat_pool.py [--broker PATH] status|pick|done ...", file=sys.stderr)
        return 1
    cmd, rest = argv[0], argv[1:]
    if cmd == "status":
        seats = json.loads(broker(path, "dump")).get("seats", {})  # unknown command: raw state
        free = [s for s in seats.values() if s.get("in_flight", 0) < 1 and not s.get("maxed_until")
                and s.get("logged_in") is not False]
        out = {"name": "seat pool", "capacity": len(seats), "available": len(free)}
    elif cmd == "pick":
        got = json.loads(broker(path, "pick"))
        if got.get("seat"):
            out = {"id": got["seat"], "via": "t3_delegate_task", "providerInstanceId": got["providerInstanceId"]}
        else:
            out = {"id": None, "reason": "paused" if got.get("paused") else "all seats busy or maxed"}
    elif cmd == "done":
        broker(path, "done", *rest)
        out = {"ok": True}
    else:
        return 1
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
