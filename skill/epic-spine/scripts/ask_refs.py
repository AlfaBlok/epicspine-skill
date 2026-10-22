"""`- [waits on [<repo>/]<code> row <id>]` references under ``## Waiting on`` (docs/doctrine/human-asks.md, D19): parse and resolve
against this repo's asks, else the sibling checkout `../<repo>`; `unknown` lists same-repo codes no ask has."""
from __future__ import annotations

import re
from pathlib import Path

import validate_spine as v

ASK_CODE = r"([A-Za-z0-9][A-Za-z0-9-]*-A\d+)"
WAIT = re.compile(r"-\s+\[waits on\s+(?:([A-Za-z0-9][\w.-]*)/)?" + ASK_CODE + r"(?:\s+row\s+(\S+))?\]\s*(.*)")


def waits(text: str) -> list[dict]:
    lines = (line.strip() for line in v.parse_sections(text).get("Waiting on", "").splitlines())
    return [{"ref": f"{r}/{c}" if r else c, "repo": r, "code": c, "row": row, "state": "unresolved"} for m in map(WAIT.fullmatch, lines) if m for r, c, row, _ in [m.groups()]]


def states(repo: Path, nodes: list[dict]) -> dict[str, str]:
    """Ask code to state: its line, else `done` when only a Decisions row cites it (the line was cleaned up)."""
    out = {a["code"]: a["state"] for n in nodes for a in n["waiting_on"] if a["code"]}
    for n in nodes:
        for code in re.findall(ASK_CODE, v.parse_sections((repo / n["path"]).read_text(encoding="utf-8", errors="replace")).get("Decisions", "")):
            out.setdefault(code, "done")
    return out


def tree_states(repo: Path) -> dict[str, str] | None:  # None: not a checkout or no root spine
    try:
        import spines
        log = spines.scan(repo, refs=False) if repo.is_dir() else {"root": None}
        return states(repo, log["nodes"]) if log["root"] else None
    except Exception:
        return None


def names(repo: Path, text: str) -> set[str]:  # what a qualified code may call this repo
    return {repo.name, *re.findall(r"(?m)^Repository:\s*(?:\S*/)?([\w.-]+)", text)}


def resolve(repo: Path, nodes: list[dict], root_text: str) -> None:
    """Set each reference's `state` to its target ask's state (open, answered, done), else `unresolved`."""
    own, mine, sibling = states(repo, nodes), names(repo, root_text), {}
    for r in (r for n in nodes for r in n["waits_on"]):
        found = own if r["repo"] in (None, *mine) else sibling.setdefault(r["repo"], tree_states(repo.parent / r["repo"]) or {})
        r["state"] = found.get(r["code"], "unresolved")


def unknown(refs: list[dict], repo: Path | None, text: str) -> list[dict]:
    """Same-repo references whose code is no ask of the tree (cross-repo ones never warn; nothing without a repo and a root spine)."""
    local = [r for r in refs if repo and r["repo"] in (None, *names(repo, text))]
    known = tree_states(repo) if local else None
    return [r for r in local if known is not None and r["code"] not in known]


def repo_root(path: Path) -> Path | None:
    return next((p for p in [path.resolve(), *path.resolve().parents] if (p / ".git").exists()), None)
