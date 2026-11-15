"""The bind view (`spines.py --bind [EPIC]`): title, deck link, Current State, Operating Learnings and open Waiting on asks of EPIC and every Parent spine up to the root.

Lean by default (agent_team E6-S119 iteration 2, folded E6-S120): each Operating Learning prints as one line (its id, date
or `applies when`, and its rule cut to about 240 characters) and `Last attempted:` keeps only its newest entry, because every
wake reads this before it works. Nothing is dropped from the spine: `spines.py --learning L-n [--bind EPIC]` prints a
learning's full text, `spines.py --bind EPIC --full` the whole view as before."""
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


RULE_MAX = 240  # characters of a learning's rule in the lean view; the full text is one --learning away
LEARNING = re.compile(r"^\s*[-*]?\s*(?:~~)?\|?\s*(L-\d+[a-z]?)\b")
PIPE_FORM = re.compile(r"^\s*[-*]?\s*\|?\s*L-\d+[a-z]?\s*\|")  # `L-n | applies when | rule | why | confirmed`


def short(text: str, cap: int = RULE_MAX) -> str:
    """TEXT cut to CAP characters: its first sentences whole, the next one cut at a word with an ellipsis."""
    text = text.strip()
    return text if len(text) <= cap else text[:cap].rsplit(" ", 1)[0].rstrip(",;:(") + " …"


def learning_line(line: str) -> str:
    """One Operating Learnings line as its index line: `- L-n (date): rule` or `- L-n | applies when | rule` (the why and dates of the pipe form dropped)."""
    if PIPE_FORM.match(line):
        cells = [c.strip() for c in line.strip().strip("|").lstrip("-* ").split("|")]
        return "- " + " | ".join([*cells[:2], short(cells[2])] if len(cells) > 2 else cells)
    m = re.match(r"^(\s*[-*]\s*(?:~~)?L-\d+[a-z]?(?:~~)?\s*(?:\([^)]*\))?(?:~~)?\s*(?:in \[[^]]*\]\([^)]*\))?\s*:?\s*)(.*)$", line)
    return m.group(1) + short(m.group(2)) if m else short(line)


def last_attempted(line: str) -> str:
    """`Last attempted:` with only its newest entry (the older ones stay in the spine and the Issue Ledger)."""
    parts = re.split(r"\s;\s*before:\s|\s;\s(?=\d{4}-\d\d-\d\d[T ])", line)
    return parts[0] + (f" ; (+{len(parts) - 1} earlier: --full)" if len(parts) > 1 else "")


def learning(repo: Path, lid: str, epic: str | None = None) -> str:
    """The full text of learning LID: in EPIC and its ancestors when given (nearest first), else in every spine of the repo."""
    cache: dict = {None: repo}
    if epic is not None:
        path, paths = epic_file(repo, epic, cache) if epic else find_root(repo, cache), []
        while path and path not in paths:
            paths.append(path)
            path = parent_file(path, cache)
    else:
        paths = [p for p in D.docs(repo) if "## Operating Learnings" in D.read(p)]
    lid = lid.upper() if lid.upper().startswith("L-") else f"L-{lid}"
    out = []
    for path in paths:
        lines = meta(path, cache)["sections"].get("Operating Learnings", "").splitlines()
        out += [f"{os.path.relpath(path, repo)}: {l.strip()}" for l in lines if (m := LEARNING.match(l)) and m.group(1).upper() == lid]
    return "\n".join(out) or f"no learning {lid} found"


def add_args(parser) -> None:
    """`--full` and `--learning` for spines.py (the lean view is the default)."""
    parser.add_argument("--full", action="store_true", help="with --bind: every learning and Last attempted entry in full (the lean view prints one line each)")
    parser.add_argument("--learning", metavar="L-N", help="print learning L-N in full (in --bind EPIC and its ancestors when given, else every spine)")


def bind(repo: Path, epic: str | None = None, full: bool = False) -> str:
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
            if lines and not full and name == "Operating Learnings" and any(LEARNING.match(l) for l in lines):
                lines = [f"(one line each, all in force; full text: spines.py --learning L-n --bind {os.path.relpath(path, cache[None])})", *(learning_line(l) for l in lines)]
            elif not full and name == "Current State":
                lines = [last_attempted(l) if l.startswith("Last attempted:") else l for l in lines]
            out += [f"## {name}", *lines] if lines else []
        path = parent_file(path, cache)
    return "\n".join(out) or "no spine found: bind from the README's first screen"


