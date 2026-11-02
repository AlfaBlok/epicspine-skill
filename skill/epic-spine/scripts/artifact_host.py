#!/usr/bin/env python3
"""Where to serve HTML/visual artifacts: prints one JSON line {host, bind, base}.

Env ``EPICSPINE_ARTIFACT_HOST`` is an override only. Unset or ``auto``: a headless
machine (not macOS/Windows, and no DISPLAY, WAYLAND_DISPLAY or x11/wayland
XDG_SESSION_TYPE) with a working Tailscale gets the MagicDNS name and
``tailscale ip -4``; anything else gets 127.0.0.1, silently. ``local`` (or
127.0.0.1) forces loopback; ``tailscale`` forces the tailnet; any other value is a
hostname and its IPv4. ``EPICSPINE_ARTIFACT_BIND`` overrides the bind. The bind
must be loopback, tailnet (100.64.0.0/10) or RFC1918; anything else, or a failed
explicit lookup, falls back to 127.0.0.1 (reason on stderr).
Stdlib only, Python 3.10+. ``--port N`` adds ``port`` and ``base`` with it.
``--serve DIR --port N`` prints that line, then runs ``python3 -m http.server N --bind <bind> --directory DIR`` in its
place: the page server for agents, never on every interface (agent_team E59-S7, audit H4). A bare
``python3 -m http.server`` (no ``--bind``) listens on every interface; the background sync reports any that does.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import socket
import subprocess
import sys

LOCAL = {"host": "127.0.0.1", "bind": "127.0.0.1"}
NETS = [ipaddress.ip_network(n) for n in (
    "127.0.0.0/8", "100.64.0.0/10", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]


def allowed(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return any(addr in net for net in NETS)


def _run(*cmd: str) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=3, check=True).stdout


def headless(env=os.environ) -> bool:
    if sys.platform in ("darwin", "win32"):
        return False
    return not (env.get("DISPLAY") or env.get("WAYLAND_DISPLAY")
                or env.get("XDG_SESSION_TYPE", "").strip().lower() in ("x11", "wayland"))


def resolve(env=os.environ) -> dict:
    mode = env.get("EPICSPINE_ARTIFACT_HOST", "").strip()
    if mode in ("local", "127.0.0.1"):
        return dict(LOCAL)
    auto = mode in ("", "auto")
    if auto:
        if not headless(env):
            return dict(LOCAL)
        mode = "tailscale"
    override = env.get("EPICSPINE_ARTIFACT_BIND", "").strip()
    try:
        if mode == "tailscale":
            host = json.loads(_run("tailscale", "status", "--json"))["Self"]["DNSName"].rstrip(".")
            bind = override or _run("tailscale", "ip", "-4").split()[0]
        else:
            host, bind = mode, override or socket.gethostbyname(mode)
        if not host or not allowed(bind):
            raise ValueError(f"bind {bind!r} is not loopback, tailnet or private")
    except Exception as exc:
        if not auto:
            print(f"artifact_host: {mode}: {exc}; using 127.0.0.1", file=sys.stderr)
        return dict(LOCAL)
    return {"host": host, "bind": bind}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int)
    parser.add_argument("--serve", metavar="DIR", help="serve DIR on the resolved bind (needs --port)")
    args = parser.parse_args(argv)
    if args.serve and not args.port:
        parser.error("--serve needs --port")
    info = resolve()
    if args.port:
        info |= {"port": args.port, "base": f"http://{info['host']}:{args.port}"}
    print(json.dumps(info), flush=True)
    if args.serve:
        if not allowed(info["bind"]):  # resolve() never returns one; a second lock on the door
            return 2
        os.execv(sys.executable, [sys.executable, "-m", "http.server", str(args.port), "--bind", info["bind"],
                                  "--directory", os.path.abspath(args.serve)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
