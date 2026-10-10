#!/usr/bin/env python3
"""Install and verify the EpicSpine always-on block (per repo, or machine-wide).

Stdlib only, Python 3.10+. Repo ``install``/``check``/``uninstall`` write the
rendered ``assets/agents-block.md`` into AGENTS.md (Codex, OpenCode, Windsurf,
Copilot, Cursor read it) and into every other harness's repo file: CLAUDE.md and
GEMINI.md get an ``@AGENTS.md`` pointer, ``.cursor/rules/epicspine.mdc`` and
``.github/copilot-instructions.md`` get a full copy. Existing content is kept;
reruns change nothing. Machine-wide ``install-global``/``check-global``/
``uninstall-global`` write the global block plus each harness's session-start
hook (``--no-hooks`` opts out); see global_install.py. ``print-hook`` and
``print-global`` emit the block for hooks and humans.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import global_install  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "assets" / "agents-block.md"
VERSION_FILE = SKILL_DIR / "VERSION"
AGENTS_NAME = "AGENTS.md"
POINTERS = ("CLAUDE.md", "GEMINI.md")
COPIES = (".cursor/rules/epicspine.mdc", ".github/copilot-instructions.md")
CURSOR_HEAD = "---\ndescription: EpicSpine always-on bind\nalwaysApply: true\n---\n\n"
BLOCK_RE = global_install.BLOCK_RE
BEGIN_RE = re.compile(r"<!-- epicspine:begin (.*?) -->")
PROFILE_RE = re.compile(r"^Dispatch profile:[ \t]*(\S.*?)[ \t]*$", re.MULTILINE)
MACHINE_FILE = ".agents/epicspine-profile.md"
ROOT_RE = re.compile(r"^Root spine: (.*?)\. Read its", re.MULTILINE)


def read_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def render(root_spine: str, version: str | None = None) -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("{version}", version or read_version())
    return text.replace("{root_spine}", root_spine)


def pointer(version: str | None = None) -> str:
    return f"<!-- epicspine:begin {version or read_version()} -->\n@{AGENTS_NAME}\n<!-- epicspine:end -->\n"


def install(repo: Path, root_spine: str) -> int:
    block = render(root_spine)
    global_install.upsert(repo / AGENTS_NAME, block)
    for name in POINTERS:
        global_install.upsert(repo / name, pointer())
    for name in COPIES:
        path = repo / name
        if name.endswith(".mdc") and not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(CURSOR_HEAD + block, encoding="utf-8")
        else:
            global_install.upsert(path, block)
    return 0


def uninstall(repo: Path) -> int:
    for name in (AGENTS_NAME, *POINTERS, *COPIES):
        path = repo / name
        global_install.remove(path)
        if name.endswith(".mdc") and path.is_file() and path.read_text(encoding="utf-8") == CURSOR_HEAD.rstrip("\n") + "\n":
            path.unlink()
    return 0


def check(repo: Path) -> int:
    agents = repo / AGENTS_NAME
    text = agents.read_text(encoding="utf-8") if agents.is_file() else ""
    match = BLOCK_RE.search(text)
    if not match:
        print(f"{AGENTS_NAME}: EpicSpine block missing")
        return 1

    problems: list[str] = []
    block = match.group(0)
    version = read_version()
    begin = BEGIN_RE.search(block)
    block_version = begin.group(1).strip() if begin else ""
    if block_version != version:
        problems.append(f"block version {block_version!r} differs from VERSION {version!r}")
    root = ROOT_RE.search(block)
    expected_full = None
    if not root:
        problems.append("block has no 'Root spine:' line")
    else:
        root_spine = root.group(1)
        if not (repo / root_spine).exists():
            problems.append(f"root spine path does not exist: {root_spine}")
        expected_full = render(root_spine, version)
        if block.rstrip("\n") + "\n" != expected_full:
            problems.append("block text differs from the rendered template")
    # Mirror files are optional, but any that carry a block must match.
    for name in (*POINTERS, *COPIES):
        path = repo / name
        found = BLOCK_RE.search(path.read_text(encoding="utf-8")) if path.is_file() else None
        want = pointer(version) if name in POINTERS else expected_full
        if found and want and found.group(0) + "\n" != want:
            problems.append(f"{name}: block is stale or edited")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def profile(repo: Path, home: Path, text: str | None) -> int:
    """Print the effective dispatch profile (repo override, machine file, unset); exit 3 if unset."""
    machine = home / MACHINE_FILE
    if text is not None:
        line = "Dispatch profile: " + " ".join(text.split())
        machine.parent.mkdir(parents=True, exist_ok=True)
        machine.write_text(line + "\n", encoding="utf-8")
        print(f"{line} (wrote ~/{MACHINE_FILE})")
        return 0
    agents = repo / AGENTS_NAME
    files = [agents]
    root = ROOT_RE.search(agents.read_text(encoding="utf-8")) if agents.is_file() else None
    if root:
        files.insert(0, repo / root.group(1))
    sources = [(f, f"repo {f.relative_to(repo) if f.is_relative_to(repo) else f}") for f in files]
    sources.append((machine, f"machine ~/{MACHINE_FILE}"))
    for path, label in sources:
        match = PROFILE_RE.search(path.read_text(encoding="utf-8")) if path.is_file() else None
        if match and (path == machine or match.group(1).lower() != "default"):
            print(f"Dispatch profile: {match.group(1)} (source: {label})")
            return 0
    print("unset")
    return 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agents_block.py", description="Install or verify the EpicSpine always-on block."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "check", "uninstall"):
        cmd = sub.add_parser(name, help=f"{name} the repo files (AGENTS.md + every harness file)")
        cmd.add_argument("--repo", type=Path, default=Path("."))
        if name == "install":
            cmd.add_argument("--root-spine", required=True)
    for name in ("install-global", "check-global", "uninstall-global"):
        cmd = sub.add_parser(name, help=f"{name.split('-')[0]} the machine-wide block and hooks")
        cmd.add_argument("--home", type=Path, help="override the home directory (tests)")
        cmd.add_argument("--claude-dir", action="append", default=[], help="Claude config dir; repeatable")
        cmd.add_argument("--no-hooks", action="store_true", help="skip session-start hooks")
    cmd = sub.add_parser("profile", help="print the effective dispatch profile; exit 3 if unset")
    cmd.add_argument("--repo", type=Path, default=Path("."))
    cmd.add_argument("--home", type=Path, help="override the home directory (tests)")
    cmd.add_argument("--set", metavar="TEXT", help="write the machine profile file")
    sub.add_parser("print-global", help="print the global block")
    sub.add_parser("print-hook", help="print the SessionStart hook JSON (used by hooks)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "install":
        return install(args.repo, args.root_spine)
    if args.command == "check":
        return check(args.repo)
    if args.command == "uninstall":
        return uninstall(args.repo)
    if args.command == "profile":
        return profile(args.repo, args.home or Path.home(), args.set)
    if args.command == "print-global":
        print(global_install.render_global(), end="")
        return 0
    if args.command == "print-hook":
        print(global_install.hook_payload())
        return 0
    home = args.home or Path.home()
    env = dict(os.environ) if args.home is None else {}
    return global_install.run(args.command.split("-")[0], home, env, args.claude_dir, not args.no_hooks)


if __name__ == "__main__":
    sys.exit(main())
