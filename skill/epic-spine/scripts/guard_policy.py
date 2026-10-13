#!/usr/bin/env python3
"""Manager-guard policy: is a Bash command or a file write delivery-manager work?

Allowlist-first. A command passes only when every simple command in it (split on
; && || | & newlines, with $(...) and backticks checked too) is read-only, an
integrate step, a spine/scratch write, a test run, a worker dispatch, or a repo's
``Manager may run:`` prefix; anything unrecognised is denied. ``check_command``
returns a reason string to deny, or None. Per-tool rules live in guard_tools.py / guard_git.py.
Stdlib only, Python 3.10+.
"""

from __future__ import annotations

import fnmatch
import os
import re
import shlex
import tempfile
from dataclasses import dataclass, field

from guard_lex import lex

READ_ONLY = set("""cat head tail less more grep egrep fgrep rg ag ack ls tree wc uniq cut tr diff cmp
comm file stat du df pwd echo printf true false test [ [[ date cal which type whoami id hostname uname
printenv basename dirname realpath readlink jq yq column nl fold fmt paste join expand rev tac od xxd
hexdump strings md5 md5sum shasum sha256sum cksum sleep wait ps pgrep lsof netstat ifconfig uptime
dig nslookup host ping export unset set local declare read : exit return man whatis journalctl
vm_stat sw_vers kill""".split())
TEST_CMDS = {"pytest", "tox", "nox", "vitest", "jest", "mocha"}
DISPATCH = {"claude", "codex", "opencode", "gemini", "aider"}
RUNNERS = {"npm", "pnpm", "yarn", "bun"}
WRITERS = {"mkdir": 0, "touch": 0, "rm": 0, "rmdir": 0, "truncate": 0, "tee": 0, "mv": 0,
           "chmod": 1, "chown": 1, "cp": -1, "ln": -1, "install": -1}
SUBCMD_OK = {  # tool -> first positional args that only read (or run tests)
    "npm": {"test", "t", "ls", "list", "view", "outdated", "why", "info"}, "pnpm": {"test", "t", "ls", "list", "why"},
    "yarn": {"test", "list", "why", "info"}, "bun": {"test"}, "cargo": {"test", "check", "clippy", "tree", "metadata"},
    "go": {"test", "vet", "list", "version", "env"}, "docker": {"ps", "images", "logs", "inspect", "version", "info"},
    "kubectl": {"get", "describe", "logs", "version", "top", "explain"}, "brew": {"list", "info", "search", "outdated", "config"},
    "pip": {"list", "show", "freeze"}, "pip3": {"list", "show", "freeze"}, "launchctl": {"list", "print"},
    "systemctl": {"status", "list-units", "is-active", "show", "cat"}, "npx": {"vitest", "jest", "mocha"},
}
PY_SCRIPTS = {"validate_spine.py", "rollup_spine.py", "skill_update.py", "agents_block.py", "url_gate.py",
              "manager_guard.py", "push_gate.py"}
PY_WRITES = re.compile(r"\bos\.(remove|unlink|rename|replace|mkdir|makedirs|rmdir|system|popen|exec\w*|spawn\w*|chmod|"
                       r"symlink|truncate|write|kill)\b|\b(subprocess|shutil|socket|requests|urllib|exec|eval|__import__|"
                       r"importlib)\b|\.(write|write_text|write_bytes|mkdir|unlink|rename|touch|rmdir)\(|open\([^)]*['\"][wax+]")
SPINE_ID = re.compile(r"^Spine ID:", re.M)
SCRATCH = re.compile(r"/\.claude[^/]*/(projects/[^/]+/memory|plans)/|/\.agents/epicspine-profile\.md$")
DEVS = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty"}
WRAPPERS = {"nohup", "time", "builtin", "exec", "command", "nice", "timeout", "env", "xargs", "watch"}
WRAP_ARG = {"nice": {"-n"}, "env": {"-u", "-C", "-S"}, "watch": {"-n"},
            "xargs": {"-n", "-I", "-P", "-L", "-d", "-E", "-s"}, "timeout": {"-s", "-k"}}


def is_dispatch(words: list[str]) -> bool:
    """Worker dispatcher call: [python3 [-B]] .../dispatcher.py <status|pick|done|bind>, or the
    machine dispatcher ($EPICSPINE_DISPATCHER / its literal env value) with status|pick|done."""
    orig, i = words, 0
    if re.fullmatch(r"python[\d.]*", os.path.basename(words[0])):
        i = 1
        while i < len(words) and words[i].startswith("-") and words[i] not in ("-c", "-m", "-"):
            i += 1
    if i < len(words) and os.path.basename(words[i]) == "dispatcher.py":
        return words[i + 1:i + 2] != [] and words[i + 1] in ("status", "pick", "done", "bind")
    words = orig
    if re.fullmatch(r"\$(EPICSPINE_DISPATCHER|\{EPICSPINE_DISPATCHER\})", words[0]):
        return words[1:2] != [] and words[1] in ("status", "pick", "done")
    try:
        argv = shlex.split(os.environ.get("EPICSPINE_DISPATCHER", ""))
    except ValueError:
        return False
    n = len(argv)
    return bool(argv) and words[:n] == argv and words[n:n + 1] != [] and words[n] in ("status", "pick", "done")


@dataclass
class Ctx:
    cwd: str
    edit_globs: list[str] = field(default_factory=list)
    run_prefixes: list[str] = field(default_factory=list)
    remote: bool = False  # an ssh remote command: read-only only
    adds: set[str] = field(default_factory=set)  # paths `git add`ed earlier in this command


def toplevel(path: str) -> str | None:
    p = os.path.abspath(path)
    while True:
        if os.path.exists(os.path.join(p, ".git")):
            return p
        if os.path.dirname(p) == p:
            return None
        p = os.path.dirname(p)


def tmp_roots() -> set[str]:
    return {os.path.realpath(t) for t in ("/tmp", "/var/tmp", tempfile.gettempdir())}


def resolve(cwd: str, p: str) -> str:
    return os.path.realpath(os.path.join(cwd, os.path.expanduser(os.path.expandvars(p))))


def path_ok(p: str, ctx: Ctx, content: str | None = None) -> bool:
    """May the manager write ``p``: scratch outside any repo, memory/plans/profile, a spine, or `Manager may edit:`."""
    if p in DEVS:
        return True
    if ctx.remote:
        return p.startswith("/tmp/")
    full = resolve(ctx.cwd, p)
    root = toplevel(os.path.dirname(full)) or ""
    if SCRATCH.search(full) or not root and any(full == t or full.startswith(t + "/") for t in tmp_roots()):
        return True
    rel = os.path.relpath(full, root) if root else full
    if rel.startswith("docs/spines/") or any(fnmatch.fnmatch(rel, g) for g in ctx.edit_globs):
        return True
    if not full.endswith(".md"):
        return False
    if content is None and os.path.isfile(full):
        with open(full, encoding="utf-8", errors="replace") as fh:
            content = fh.read(8192)
    return bool(content and SPINE_ID.search(content))


def unwrap(words: list[str]) -> list[str]:
    """Drop env assignments and wrappers (nohup, timeout 5, env X=1, xargs -n1 ...)."""
    while words:
        if re.match(r"^[A-Za-z_]\w*=", words[0]):
            words = words[1:]
            continue
        name = os.path.basename(words[0])
        if name not in WRAPPERS or (name == "command" and words[1:2] in (["-v"], ["-V"])):
            return words
        i = 1
        while i < len(words) and (words[i].startswith("-") or re.match(r"^[A-Za-z_]\w*=", words[i])):
            i += 2 if words[i] in WRAP_ARG.get(name, ()) else 1
        if name == "timeout" and i < len(words):
            i += 1
        words = words[i:] + (["{}"] if name == "xargs" and words[i:] else [])  # xargs feeds unseen args
    return words


def check_command(cmd: str, ctx: Ctx) -> str | None:
    """Reason to deny ``cmd`` for the manager, or None when every part is allowed."""
    try:
        segs = lex(cmd)
    except Exception:  # noqa: BLE001 - unparseable means unverifiable
        return "the command could not be parsed"
    for words, redirs, body in segs:
        for op, target in redirs:
            if ">" in op and not (op == ">&" and re.fullmatch(r"\d+|-", target)) and not path_ok(target, ctx):
                return f"it writes to `{target}`"
        why = check_simple(unwrap(words), body, ctx)
        if why:
            return why
    return None


def check_simple(words: list[str], body: str | None, ctx: Ctx) -> str | None:
    from guard_tools import RULES  # local import: guard_tools imports this module
    if not words or words[0] in ("for", "case", "esac", "select", "function"):
        return None  # loop/case headers run nothing themselves
    if words[0] in ("!", "{", "}", "then", "do", "else", "elif", "fi", "done", "if", "while", "until"):
        return check_simple(words[1:], body, ctx)
    joined = " ".join(words)
    if not ctx.remote and any(joined == p or joined.startswith(p + " ") for p in ctx.run_prefixes):
        return None
    if not ctx.remote and is_dispatch(words):
        return None
    name, args = os.path.basename(words[0]), words[1:]
    pos = [a for a in args if not a.startswith("-")]
    if name in ("cd", "pushd"):
        ctx.cwd = resolve(ctx.cwd, pos[0] if pos else "~")
        return None
    if name in READ_ONLY:
        return None
    if name in RULES:
        return RULES[name](args, body, ctx)
    if name in WRITERS:
        skip = WRITERS[name]
        targets = pos[-1:] if skip < 0 else pos[skip:]
        bad = [t for t in targets if not path_ok(t, ctx)]
        return f"`{name}` writes `{bad[0]}`" if bad else None
    if ctx.remote:
        return f"`{name}` is not on the read-only allowlist for remote commands"
    if name in TEST_CMDS or name in DISPATCH:
        return None
    if name in SUBCMD_OK and pos and (pos[0] in SUBCMD_OK[name] or pos[0] == "run" and name in RUNNERS
                                      and re.search(r"test|check|lint", " ".join(pos[1:2]))):
        return None
    if name == "make" and pos and all(re.search(r"test|check|lint", p) for p in pos):
        return None
    return f"`{name}{' ' + pos[0] if name in SUBCMD_OK and pos else ''}` is not on the manager allowlist"
