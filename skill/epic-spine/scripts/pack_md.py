"""Pack files as Markdown (references/packs.md): find a section by heading, read its table or list items.

Shared by pack_validate.py and pack_init.py. A reader is a function `repo path -> text or None`: the working tree,
the index (`git show :path`) or HEAD."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(\S.*)$")
SEP = re.compile(r":?-+:?")


def worktree(repo: Path):
    def read(rel: str) -> str | None:
        p = repo / rel
        return p.read_text(encoding="utf-8") if p.is_file() else None
    return read


def git_reader(repo: Path, rev: str):
    """`rev` "" reads the index, "HEAD" the last commit; None when the file (or the repo, or HEAD) is not there."""
    def read(rel: str) -> str | None:
        r = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{rel}"], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None
    return read


def where(file: dict, section: dict) -> str:
    """The repo path a section lives in: its own `path`, else its file's."""
    return section.get("path", file["path"])


def body(text: str | None, heading: str | None) -> str | None:
    """A section's text under `## heading` (up to the next heading of its level or higher); heading None = whole file."""
    if text is None:
        return None
    if heading is None:
        return text
    lines, fence = text.splitlines(), False
    for i, line in enumerate(lines):
        fence ^= line.lstrip().startswith("```")
        m = None if fence else HEADING.match(line)
        if m and len(m.group(1)) >= 2 and m.group(2).strip().lower() == heading.strip().lower():
            out = []
            for nxt in lines[i + 1:]:
                n = HEADING.match(nxt)
                if n and len(n.group(1)) <= len(m.group(1)):
                    break
                out.append(nxt)
            return "\n".join(out)
    return None


def cells(line: str) -> list[str]:
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def table(text: str | None) -> tuple[list[str], list[dict[str, str]]] | None:
    """(header, rows as column -> cell) of the first table in `text`; None when there is none."""
    lines = (text or "").splitlines()
    i = next((n for n, line in enumerate(lines) if line.lstrip().startswith("|")), len(lines))
    if i + 1 >= len(lines) or not all(SEP.fullmatch(c) for c in cells(lines[i + 1])):
        return None
    head, rows = cells(lines[i]), []
    for line in lines[i + 2:]:
        if not line.lstrip().startswith("|"):
            break
        vals = cells(line)
        rows.append(dict(zip(head, vals + [""] * (len(head) - len(vals)))))
    return head, rows


def items(text: str | None) -> list[str]:
    """List items (`- x`, `* x`, `1. x`) of a list section."""
    return [m.group(1).strip() for line in (text or "").splitlines() if (m := ITEM.match(line))]
