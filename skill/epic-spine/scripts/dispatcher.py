#!/usr/bin/env python3
"""Machine dispatcher client: status | pick [--task T] | done ID [--fail] [--signal T] | bind.

Runs the command in env EPICSPINE_DISPATCHER (shlex-split), validates its JSON
against the contract in references/machine-dispatcher.md, and passes it through.
Unset (or repo opt-out ``Dispatch profile: local-only``): prints {"active": false}.
Failure: prints {"error": "..."} and exits 2. Stdlib only, Python 3.10+.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

TIMEOUT = 20
VIAS = {"t3_delegate_task": ("providerInstanceId",), "native_subagent": (), "command": ("argv",)}
OPT_OUT = re.compile(r"^[\s>*-]*Dispatch profile:\**\s*`?local-only\b", re.I | re.M)
ROOT_RE = re.compile(r"Root spine:\s*(\S+?)\.?\s", re.I)


class Fail(Exception):
    pass


def local_only(repo: Path) -> bool:
    agents = repo / "AGENTS.md"
    text = agents.read_text(encoding="utf-8") if agents.is_file() else ""
    files = [agents]
    root = ROOT_RE.search(text + "\n")
    if root:
        files.append(repo / root.group(1).strip("`"))
    return any(f.is_file() and OPT_OUT.search(f.read_text(encoding="utf-8")) for f in files)


def call(args: list[str]) -> dict:
    cmd = shlex.split(os.environ["EPICSPINE_DISPATCHER"])
    try:
        proc = subprocess.run([*cmd, *args], capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        raise Fail(f"dispatcher timed out after {TIMEOUT}s")
    except (OSError, ValueError) as exc:
        raise Fail(f"cannot run dispatcher: {exc}")
    if proc.returncode:
        raise Fail(f"dispatcher exited {proc.returncode}: {proc.stderr.strip()[:200]}")
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        raise Fail("dispatcher output is not JSON")
    if not isinstance(data, dict):
        raise Fail("dispatcher output is not a JSON object")
    return data


def check(sub: str, data: dict) -> None:
    if sub == "status":
        ok = isinstance(data.get("name"), str) and all(
            isinstance(data.get(k), int) and not isinstance(data.get(k), bool) for k in ("capacity", "available"))
        if not ok:
            raise Fail("status needs name (str), capacity (int), available (int)")
    elif sub == "pick" and data.get("id") is not None:
        if not isinstance(data["id"], str) or not data["id"]:
            raise Fail("pick id must be a non-empty string or null")
        need = VIAS.get(data.get("via"))
        if need is None:
            raise Fail(f"unknown via: {data.get('via')!r}")
        missing = [k for k in need if not data.get(k)]
        if missing:
            raise Fail(f"via {data['via']} missing {', '.join(missing)}")
    elif sub == "done" and data.get("ok") is not True:
        raise Fail("done must return {\"ok\": true}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="dispatcher.py")
    p.add_argument("--repo", type=Path, default=Path("."))
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("bind")
    pick = sub.add_parser("pick")
    pick.add_argument("--task")
    done = sub.add_parser("done")
    done.add_argument("id")
    done.add_argument("--fail", action="store_true")
    done.add_argument("--signal")
    a = p.parse_args(argv)
    if not os.environ.get("EPICSPINE_DISPATCHER", "").strip() or local_only(a.repo):
        if a.cmd != "bind":
            print(json.dumps({"active": False}))
        return 0
    try:
        if a.cmd == "pick":
            data = call(["pick", *(["--task", a.task] if a.task else [])])
        elif a.cmd == "done":
            data = call(["done", a.id, *(["--fail"] if a.fail else []),
                         *(["--signal", a.signal] if a.signal else [])])
        else:
            data = call(["status"])
        check("status" if a.cmd == "bind" else a.cmd, data)
    except Fail as exc:
        if a.cmd == "bind":
            print(" · dispatch: unavailable → native subagent")
            return 0
        print(json.dumps({"error": str(exc)}))
        return 2
    print(f" · dispatch: {data['name']} ({data['capacity']} seats)" if a.cmd == "bind" else json.dumps(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
