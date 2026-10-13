#!/usr/bin/env python3
"""Machine-wide EpicSpine install: write the global bind block into every detected
harness's user-level instruction file and register its session-start hook; Claude
Code also gets the enforcement hooks in MANAGED (``hooks=False`` opts out).
Stdlib only, Python 3.10+. One block, one marker pair, one adapter table."""

from __future__ import annotations

import json
import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
GLOBAL_TEMPLATE = SKILL_DIR / "assets" / "global-block.md"
BLOCK_RE = re.compile(r"<!-- epicspine:begin [^>]*-->.*?<!-- epicspine:end -->", re.DOTALL)
# (event, script + args, matcher, claude-code only): every hook EpicSpine manages.
MANAGED = (("SessionStart", "agents_block.py print-hook", None, False),
           ("Stop", "url_gate.py", None, True),
           ("Stop", "push_gate.py", None, True),
           ("PreToolUse", "manager_guard.py", "Bash|Edit|Write|MultiEdit|NotebookEdit|mcp__.*", True))
UNSUPPORTED = {
    "cursor (user level)": "user rules live in the app settings UI, not a file; repo install writes .cursor/rules",
    "aider": "no user-level instruction file; needs a read: entry in .aider.conf.yml",
    "codex hook": "no verified session-start hook mechanism; instruction file only",
    "opencode hook": "hooks need a JS plugin; instruction file only",
}


def read_version() -> str:
    return (SKILL_DIR / "VERSION").read_text(encoding="utf-8").strip()


def render_global() -> str:
    return GLOBAL_TEMPLATE.read_text(encoding="utf-8").replace("{version}", read_version())


def hook_payload() -> str:
    ctx = render_global()
    return json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}})


def upsert(path: Path, block: str) -> str:
    """Write ``block`` into ``path``; returns created|updated|appended|current."""
    old = path.read_text(encoding="utf-8") if path.is_file() else None
    if old is None:
        new, how = block, "created"
    elif BLOCK_RE.search(old):
        new, how = BLOCK_RE.sub(lambda _: block.rstrip("\n"), old), "updated"
    else:
        new, how = old.rstrip("\n") + "\n\n" + block, "appended"
    if new == old:
        return "current"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new, encoding="utf-8")
    return how


def remove(path: Path) -> bool:
    """Strip the EpicSpine block; delete the file if nothing else remains."""
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    match = BLOCK_RE.search(text)
    if not match:
        return False
    before, after = text[: match.start()].rstrip("\n"), text[match.end() :].strip("\n")
    rest = before + ("\n\n" if before and after else "") + after
    path.write_text(rest + "\n", encoding="utf-8") if rest else path.unlink()
    return True


def harnesses(home: Path, env: dict, claude_dirs: list[str]):
    """Yield (label, detect_path, instruction_file, explicit, hook_settings|None)."""
    found: list[Path] = [Path(d).expanduser() for d in claude_dirs]
    explicit = bool(found)
    if not explicit:
        if env.get("CLAUDE_CONFIG_DIR"):
            found.append(Path(env["CLAUDE_CONFIG_DIR"]).expanduser())
        for p in sorted(home.glob(".claude*")):
            if p.is_dir() and (p.name == ".claude" or (p / "settings.json").exists()
                               or (p / "projects").is_dir()):
                found.append(p)
    for d in dict.fromkeys(found):
        yield f"claude-code[{d}]", d, d / "CLAUDE.md", explicit, d / "settings.json"
    xdg = Path(env.get("XDG_CONFIG_HOME") or home / ".config")
    codex = Path(env.get("CODEX_HOME") or home / ".codex")
    gem, ws = home / ".gemini", home / ".codeium" / "windsurf"
    yield "codex", codex, codex / "AGENTS.md", False, None
    yield "opencode", xdg / "opencode", xdg / "opencode" / "AGENTS.md", False, None
    yield "gemini-cli", gem, gem / "GEMINI.md", False, gem / "settings.json"
    yield "windsurf", ws, ws / "memories" / "global_rules.md", False, None
    yield "copilot-cli", home / ".copilot", home / ".copilot" / "copilot-instructions.md", False, None


def _load(settings: Path) -> dict:
    if not settings.is_file():
        return {}
    data = json.loads(settings.read_text(encoding="utf-8") or "{}")
    if not isinstance(data, dict):
        raise ValueError("settings.json is not a JSON object")
    return data


def _mark(script: str) -> str:
    name, _, args = script.partition(" ")
    return f'{name}"' + (f" {args}" if args else "")


def _strip_hook(data: dict) -> bool:
    """Remove EpicSpine-managed hooks (see MANAGED); foreign hooks stay."""
    changed = False
    for event in dict.fromkeys(e for e, *_ in MANAGED):
        marks = [_mark(s) for e, s, *_ in MANAGED if e == event]
        groups = data.get("hooks", {}).get(event)
        if not isinstance(groups, list):
            continue
        hit = False
        for group in list(groups):
            hooks = group.get("hooks") if isinstance(group, dict) else None
            keep = None if not isinstance(hooks, list) else [
                h for h in hooks if not any(m in str(h.get("command", "")) for m in marks)]
            if keep is not None and len(keep) != len(hooks):
                hit = changed = True
                group["hooks"] = keep
                if not keep:
                    groups.remove(group)
        if hit and not groups:
            del data["hooks"][event]
    if changed and not data["hooks"]:
        del data["hooks"]
    return changed


def set_hook(settings: Path, on: bool, stop: bool = False) -> str:
    """Add/remove managed hooks (SessionStart; plus the Claude-only ones if ``stop``), merging."""
    try:
        data = _load(settings)
    except (ValueError, OSError) as exc:
        return f"error: cannot merge {settings}: {exc}"
    if not _strip_hook(data) and not on:
        return "absent"
    for event, script, matcher, claude_only in MANAGED if on else ():
        if stop or not claude_only:
            group = {"matcher": matcher} if matcher else {}
            group["hooks"] = [{"type": "command", "command": f'python3 "{Path(__file__).parent}/{_mark(script)}'}]
            data.setdefault("hooks", {}).setdefault(event, []).append(group)
    if data:
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    elif settings.exists():
        settings.unlink()
    return "set" if on else "removed"


def has_hook(settings: Path, stop: bool = False) -> bool:
    try:
        hooks = str(_load(settings).get("hooks", {}))
    except (ValueError, OSError):
        return False
    return all(_mark(s) in hooks for _, s, _, claude_only in MANAGED if stop or not claude_only)


def run(action: str, home: Path, env: dict, claude_dirs: list[str], hooks: bool = True) -> int:
    """action: install | check | uninstall. Prints one line per harness."""
    block, code, present = render_global(), 0, 0
    for label, detect, target, explicit, settings in harnesses(home, env, claude_dirs):
        if not (detect.exists() or (explicit and action == "install")):
            print(f"{label}: not detected ({detect} absent)")
            continue
        present += 1
        if action == "install":
            line = f"{label}: {upsert(target, block)} {target}"
        elif action == "uninstall":
            line = f"{label}: {'removed' if remove(target) else 'absent'} {target}"
        else:
            text = target.read_text(encoding="utf-8") if target.is_file() else ""
            match = BLOCK_RE.search(text)
            state = "missing" if not match else ("current" if match.group(0) + "\n" == block else "stale")
            code |= state != "current"
            line = f"{label}: {state} {target}"
        if settings is not None:
            stop = label.startswith("claude-code")
            if action == "check" and hooks:
                ok = has_hook(settings, stop)
                code |= not ok
                line += f"; hook {'present' if ok else 'missing'}"
            elif action == "uninstall" or (action == "install" and hooks):
                result = set_hook(settings, action == "install", stop)
                code |= result.startswith("error")
                line += f"; hook {result}"
        print(line)
    for name, reason in UNSUPPORTED.items():
        print(f"{name}: unsupported: {reason}")
    if not present:
        print("no supported harness detected; nothing done")
        return 1 if action != "uninstall" else 0
    return int(code)
