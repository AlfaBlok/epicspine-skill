#!/usr/bin/env python3
"""Server-like local processes for local_mess.py: ``/proc`` on Linux, ``ps`` + ``lsof`` on macOS (best effort, bounded)."""

from __future__ import annotations

import contextlib
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Callable, NamedTuple

SERVER_AFTER = 24 * 3600
PROC = Path("/proc")
SERVER_RE = re.compile(r"(?:^|\s)(?:\S*/)?(?:http\.server|SimpleHTTPServer|http-server|live-server|serve|httpd)(?:\s|$)|\bphp\b.* -S ")


class Proc(NamedTuple):
    pid: int
    cwd: str
    args: list[str]
    age: float  # seconds running
    listens: tuple[str, ...] | None = None  # "<addr>:<port>" it listens on (Linux /proc); None: unknown, judged by its args


def serving_dir(proc: Proc) -> str:
    args = proc.args
    for i, arg in enumerate(args):
        value = arg.split("=", 1)[1] if arg.startswith("--directory=") else args[i + 1] if arg in ("-d", "--directory") and i + 1 < len(args) else None
        if value:
            return os.path.realpath(os.path.join(proc.cwd, value))
    return os.path.realpath(proc.cwd)


def server_lines(name: str, paths: list[Path], procs: list[Proc]) -> list[str]:
    roots, lines = [p.resolve() for p in paths], []
    for proc in procs:
        if proc.age < SERVER_AFTER or not SERVER_RE.search(" ".join(proc.args)):
            continue
        where = Path(serving_dir(proc))
        if any(where == r or r in where.parents for r in roots):
            lines.append(f"{name}: http server pid {proc.pid} serving {where} for {max(1, int(proc.age // 86400))}d — stop it when done")
    return lines


EVERY = {"", "0.0.0.0", "::", "[::]", "*", "0"}
BIND_FLAGS = {"-b", "--bind", "-a", "--address", "-l", "--listen", "-S"}


def bind_of(args: list[str]) -> str | None:
    """The address a server-like process listens on: its ``--bind``/``-b`` (http.server), ``-a`` (http-server), ``-l``
    (serve) or ``-S host:port`` (php) value, "" when it names none (these servers then listen on every interface);
    None for ``httpd``, whose bind lives in its config."""
    if any(os.path.basename(a) == "httpd" for a in args):
        return None
    for i, arg in enumerate(args):
        flag, _, inline = arg.partition("=")
        if flag in BIND_FLAGS and (inline or i + 1 < len(args)):
            value = inline or args[i + 1]
            value = value.removeprefix("tcp://")
            if flag in ("-l", "--listen", "-S") or (value.count(":") == 1 and not value.startswith("[")):
                value = "" if value.isdigit() else value.rsplit(":", 1)[0]
            return value
    return ""


def public_lines(procs: list[Proc], helper: str) -> list[str]:
    """One line per server-like process, at any age and in any directory, that listens on every interface (agent_team E59-S7,
    audit H4: on a host with a public IP that publishes whatever it serves). Its real sockets when known, else its args."""
    lines = []
    for proc in procs:
        if proc.listens is not None:
            wild = [a for a in proc.listens if a.rsplit(":", 1)[0] in ("0.0.0.0", "[::]")]
            how = f"listening on {', '.join(wild)}" if wild else None
        else:
            bind = bind_of(proc.args) if SERVER_RE.search(" ".join(proc.args)) else None
            how = None if bind is None or bind.strip("[]") not in EVERY else f"--bind {bind}" if bind else "no bind address"
        if how:
            lines.append(f"http server pid {proc.pid} listens on every interface ({how}) serving {serving_dir(proc)} — stop it and "
                         f"serve on the tailnet or 127.0.0.1: `{helper} --serve <dir> --port <n>`")
    return lines


def parse_etime(text: str) -> float:
    """``[[dd-]hh:]mm:ss`` (ps etime) in seconds."""
    days, _, rest = text.rpartition("-")
    parts = [int(p) for p in rest.split(":")]
    secs = 0
    for part in parts:
        secs = secs * 60 + part
    return float(secs + int(days or 0) * 86400)


def listening(root: Path) -> dict[str, str]:
    """socket inode -> "<addr>:<port>" for every listening TCP socket (``/proc/net/tcp`` and ``tcp6``; only wildcard
    addresses are spelled out, others are "host")."""
    found = {}
    for name, wild in (("tcp", "0" * 8), ("tcp6", "0" * 32)):
        with contextlib.suppress(OSError):
            for line in (root / "net" / name).read_text().splitlines()[1:]:
                cols = line.split()
                if len(cols) > 9 and cols[3] == "0A":
                    addr, port = cols[1].split(":")
                    found[cols[9]] = f"{('0.0.0.0' if name == 'tcp' else '[::]') if addr == wild else 'host'}:{int(port, 16)}"
    return found


def sockets(entry: Path, table: dict[str, str]) -> tuple[str, ...] | None:
    """What a pid listens on, from its ``fd`` links; None when they cannot be read."""
    try:
        links = [os.readlink(fd) for fd in (entry / "fd").iterdir()]
    except OSError:
        return None
    return tuple(sorted({table[link[8:-1]] for link in links if link.startswith("socket:[") and link[8:-1] in table}))


def scan_proc(root: Path, now: float, hz: int | None = None) -> list[Proc]:
    hz = hz or os.sysconf("SC_CLK_TCK")
    table = listening(root)
    boot = next(int(line.split()[1]) for line in (root / "stat").read_text().splitlines() if line.startswith("btime"))
    found = []
    for entry in root.iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            args = [a for a in (entry / "cmdline").read_bytes().decode(errors="replace").split("\0") if a]
            if not SERVER_RE.search(" ".join(args)):
                continue
            started = boot + int((entry / "stat").read_text().rsplit(")", 1)[1].split()[19]) / hz
            found.append(Proc(int(entry.name), os.readlink(entry / "cwd"), args, now - started, sockets(entry, table) if table else None))
        except (OSError, ValueError, IndexError):
            continue
    return found


def run_cmd(cmd: list[str], seconds: float = 8.0) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=seconds).stdout
    except (subprocess.TimeoutExpired, OSError):
        return ""


def scan_ps(run: Callable[[list[str]], str]) -> list[Proc]:
    """macOS best effort: ``ps`` for age and args, ``lsof -d cwd`` only for the long-running server-like pids."""
    cand = {}
    for line in run(["ps", "-axo", "pid=,etime=,args="]).splitlines():
        parts = line.split(None, 2)
        with contextlib.suppress(ValueError):
            if len(parts) == 3 and parts[0].isdigit() and SERVER_RE.search(parts[2]) and parse_etime(parts[1]) >= SERVER_AFTER:
                cand[int(parts[0])] = (parse_etime(parts[1]), parts[2])
    if not cand:
        return []
    cwds, pid = {}, 0
    for line in run(["lsof", "-a", "-d", "cwd", "-Fpn", "-p", ",".join(map(str, cand))]).splitlines():
        if line.startswith("p") and line[1:].isdigit():
            pid = int(line[1:])
        elif line.startswith("n") and pid:
            cwds[pid] = line[1:]
    return [Proc(pid, cwds[pid], shlex.split(args) if "'" in args or '"' in args else args.split(), age) for pid, (age, args) in cand.items() if pid in cwds]


def scan(now: float, root: Path = PROC, run: Callable[[list[str]], str] = run_cmd) -> list[Proc]:
    """Server-like processes (Linux ``/proc`` under ``root``, else ps/lsof via ``run``); [] on any failure."""
    try:
        return scan_proc(root, now) if (root / "stat").is_file() else scan_ps(run)
    except Exception:
        return []
