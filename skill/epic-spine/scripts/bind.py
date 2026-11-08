"""The bind view (`spines.py --bind [EPIC]`): title, deck link, Current State, Operating Learnings and open Waiting on asks of EPIC and every Parent spine up to the root."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doctrine as D  # noqa: E402
from spines import find_root, meta, parent_file  # noqa: E402


def epic_file(repo: Path, epic: str, cache: dict) -> Path | None:
    """EPIC as a path (cwd or repo relative), else as a code (`EPIC-4`, `4`) matched against the file name or the `# EPIC-4:` title."""
    path = next((p.resolve() for p in (Path(epic), repo / epic) if p.is_file()), None)
    code = epic.upper() if epic.upper().startswith("EPIC-") else f"EPIC-{epic}"
    named = lambda p: re.match(re.escape(code) + r"\b(?!\d)", p.stem.upper()) or re.search(rf"(?m)^# {re.escape(code)}\b(?!\d)", meta(p, cache)["text"].upper())
    return path or next((p for p in D.docs(repo) if D.is_epic(D.read(p)) and named(p)), None)


def deck_template(repo: Path, cache: dict) -> str | None:
    """The repo value `Epic deck: <URL with {code}>` (AGENTS.md, else the root spine): where each epic's human deck lives."""
    root = find_root(repo, cache)
    for text in ((repo / "AGENTS.md").read_text(errors="replace") if (repo / "AGENTS.md").is_file() else "", meta(root, cache)["text"] if root else ""):
        for line in re.findall(r"(?im)^[ \t>*_-]*epic deck[*_ ]*:[*_ \t`]*(.*)$", text):
            url = line.replace("`", " ").split()[0].rstrip(".,;") if line.strip() else ""
            if url.startswith(("http://", "https://")) and "{code}" in url:
                return url
    return None


def deck_code(path: Path, title: str) -> str:
    """An epic's deck code, as the console names it: its title's code (EPIC-47, M6), else its file name (`root`)."""
    m = re.match(r"#\s+(EPIC-\d+|M\d+)\b", title, re.IGNORECASE)
    return m.group(1).upper() if m else path.stem


def bind(repo: Path, epic: str | None = None) -> str:
    """The bind view: title, Current State, Operating Learnings and open Waiting on asks of the epic and every Parent spine up to the root."""
    cache: dict = {None: repo}
    path = epic_file(repo, epic, cache) if epic else find_root(repo, cache)
    out: list[str] = []
    deck = deck_template(repo, cache)
    while (m := path and meta(path, cache)) and path not in cache.setdefault("seen", set()):  # a parent cycle ends here
        cache["seen"].add(path)
        title = next((l for l in m["text"].splitlines() if l.startswith("# ")), m["id"])
        out.append(f"== {os.path.relpath(path, cache[None])}: " + title)
        if deck:  # agent_team E47-S4 r4: an agent working inside an epic reads its deck first
            out.append("Deck (read it first): " + deck.replace("{code}", deck_code(path, title)))
        for name in ("Current State", "Operating Learnings", "Waiting on"):
            lines = [l for l in m["sections"].get(name, "").splitlines() if l.strip() and not (name == "Waiting on" and re.search(r"\[(answered|feedback|superseded)\b|^none\b", l.lstrip("- ")))]
            out += [f"## {name}", *lines] if lines else []
        path = parent_file(path, cache)
    return "\n".join(out) or "no spine found: bind from the README's first screen"


