#!/usr/bin/env python3
"""Manager-guard rules for non-git tools (curl, wget, ssh, python, shells, find,
sed, awk, sort, pkill, open, source). Each takes (args, heredoc body, Ctx) and
returns a deny reason or None; ``RULES`` maps command names to rules. ssh is
allowed only with a remote command that passes the read-only policy.
Stdlib only, Python 3.10+.
"""

from __future__ import annotations

import os
import re

from guard_git import gh, git
from guard_policy import PY_SCRIPTS, PY_WRITES, Ctx, check_command, check_simple, path_ok


def curl(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    i = 0
    while i < len(args):
        a, nxt = args[i], (args[i + 1] if i + 1 < len(args) else "")
        i += 1
        if a.startswith("--"):
            name, _, val = a.partition("=")
            if name in ("--data", "--data-raw", "--data-binary", "--data-urlencode", "--form", "--json",
                        "--upload-file", "--remote-name", "--remote-name-all", "--config") or name.startswith("--data"):
                return f"`curl {name}` sends or writes data"
            if name == "--request" and (val or nxt).upper() not in ("GET", "HEAD"):
                return "curl with a non-GET method is worker work"
            if name in ("--output", "--dump-header", "--cookie-jar") and not path_ok(val or nxt, ctx):
                return f"curl writes `{val or nxt}`"
        elif a.startswith("-") and len(a) > 1:
            for j, ch in enumerate(a[1:]):
                val = a[j + 2:] or nxt
                if ch in "dFTOKQ":
                    return f"`curl -{ch}` sends or writes data"
                if ch == "X" and val.upper() not in ("GET", "HEAD"):
                    return "curl with a non-GET method is worker work"
                if ch in "oDc" and not path_ok(val, ctx):
                    return f"curl writes `{val}`"
                if ch in "XoDcHwmAeburxYyzECUQ":
                    i += 0 if a[j + 2:] else 1
                    break
    return None


def wget(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    ok = "--spider" in args or any(a in ("-O-", "-qO-", "-O", "--output-document=-") for a in args) and (
        "-O" not in args or args[args.index("-O") + 1:][:1] == ["-"])
    return None if ok else "wget downloads files; use curl GET or a worker"


SSH_VALUE = set("BbcDEeFIiJLlmOopQRSWw")


def ssh(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if len(args[i]) == 2 and args[i][1] in SSH_VALUE else 1
    rest = args[i + 1:]
    if not rest and body is None:
        return "interactive ssh cannot be checked; give a read-only remote command or dispatch a worker"
    why = check_command(" ".join(rest), Ctx(cwd="/", remote=True)) if rest else None
    if not why and rest and os.path.basename(rest[0]) in ("bash", "sh", "zsh") and "-c" not in rest and body:
        why = check_command(body, Ctx(cwd="/", remote=True))
    return f"ssh remote command not read-only: {why}" if why else None


def python(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    i = 0
    while i < len(args) and args[i].startswith("-") and args[i] not in ("-c", "-m", "-"):
        i += 2 if args[i] in ("-W", "-X") else 1
    first = args[i] if i < len(args) else None
    if first == "-m" and i + 1 < len(args):
        mod, rest = args[i + 1], " ".join(args[i + 2:])
        if mod == "http.server" and not ctx.remote:
            return None if re.search(r"(-b|--bind)[= ](127\.0\.0\.1|localhost|::1)\b", rest) else \
                "serve status pages on 127.0.0.1 only: add --bind 127.0.0.1"
        if mod in ("unittest", "pytest", "doctest") and not ctx.remote or mod == "json.tool":
            return None
        if mod in ("pip", "pip3"):
            return check_simple(["pip", *args[i + 2:]], body, ctx)
        return f"`python -m {mod}` is not on the manager allowlist"
    if first not in (None, "-c", "-"):
        return None if os.path.basename(first) in PY_SCRIPTS and not ctx.remote else \
            f"running `{os.path.basename(first)}` is worker work (only EpicSpine scripts are allowed)"
    code = (args[i + 1] if i + 1 < len(args) else "") if first == "-c" else body
    if code is None:
        return "python reading an unseen script is worker work"
    return "python code that may change state is worker work" if PY_WRITES.search(
        re.sub(r"sys\.std(out|err)\.write", "", code)) else None


def shell(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    if "-c" in args and args.index("-c") + 1 < len(args):
        return check_command(args[args.index("-c") + 1], ctx)
    if not [a for a in args if not a.startswith("-")] and body is not None:
        return check_command(body, ctx)
    return "running a shell script is worker work"


def find(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    for k, a in enumerate(args):
        if a in ("-delete", "-fprint", "-fprint0", "-fprintf", "-fls", "-ok", "-okdir"):
            return f"`find {a}` changes files"
        if a in ("-exec", "-execdir"):
            end = next((j for j in range(k + 1, len(args)) if args[j] in (";", "+")), len(args))
            why = check_simple(args[k + 1:end], None, ctx)
            if why:
                return why
    return None


def sed(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    bad = any(a.startswith("--in-place") or re.match(r"^-[a-zA-Z]*i", a) for a in args)
    return "`sed -i` edits files in place" if bad else None


def awk(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    bad = any(re.search(r"system\s*\(|getline|print[^;{}]*>", a) for a in args)
    return "awk program writes files or runs commands" if bad else None


def sort(args: list[str], body: str | None, ctx: Ctx) -> str | None:
    for k, a in enumerate(args):
        target = args[k + 1] if a == "-o" and k + 1 < len(args) else a[9:] if a.startswith("--output=") else None
        if target is not None and not path_ok(target, ctx):
            return f"sort writes `{target}`"
    return None


RULES = {"git": git, "gh": gh, "curl": curl, "wget": wget, "ssh": ssh, "find": find, "sed": sed, "gsed": sed,
         "awk": awk, "gawk": awk, "sort": sort, "bash": shell, "sh": shell, "zsh": shell,
         "pkill": lambda a, b, c: None if "http.server" in " ".join(a) else "pkill only for http.server status pages",
         "killall": lambda a, b, c: "killall is worker work",
         "open": lambda a, b, c: None if all(x.startswith(("http://", "https://", "-")) for x in a) else
         "open only for http(s) URLs",
         "source": lambda a, b, c: None if a and a[0].endswith("activate") else "sourcing scripts is worker work",
         **{f"python{v}": python for v in ("", "3", "3.10", "3.11", "3.12", "3.13", "3.14")}}
RULES["."] = RULES["source"]
