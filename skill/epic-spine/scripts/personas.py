#!/usr/bin/env python3
"""Persona files (``personas/<name>.md``) and epic Team tables (references/personas.md): format rules and the assignee check.

Pure helpers over text and parsed table rows (validate_spine.py and spines.py call them); ``personas.py FILE...`` prints each file's errors (exit 1 on any) and warnings (a ``skills:`` name missing from the repo's ``skills/team-skills.json``)."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from claim import CLOSED, LEASE

FRONT = ("name", "template", "model", "host")
BODY = ("Remit", "Reads", "Writes")
FORBIDDEN = {"goal", "cadence", "write scope"}  # assignment, not identity: lives in the epic's Team table
TEAM_COLUMNS = ("Persona", "Cadence", "Write scope")
HUMAN = "jordi"
OPEN = {"ready", "active", "blocked", "review", "testing"}
SKILL = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MANIFEST = Path("skills") / "team-skills.json"


def slug(value: str) -> str:
    """``[Delivery Manager](x.md) (acts as Fixer)`` -> ``delivery-manager``: how files, Team cells and assignees are compared."""
    value = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", value)
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"\(.*", "", value).lower()).strip("-")


def base(header: list[str]) -> dict[str, str]:
    """Table header -> its name without a trailing ``(…)``: ``Cadence (console)`` counts as ``Cadence``."""
    return {re.sub(r"\s*\(.*\)\s*$", "", h).strip(): h for h in header}


def is_file(path: Path, text: str) -> bool:
    return path.parent.name == "personas" and text.startswith("---")


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Flat ``key: value`` pairs; a block list (``key:`` then ``- item`` lines) folds into ``[item, item]``."""
    head, _, body = text[3:].partition("\n---") if text.startswith("---") else ("", "", text)
    out: dict[str, str] = {}
    key = None
    for line in head.splitlines():
        item = re.match(r"^\s*-\s+(.*)$", line)
        if item and key and (not out[key] or out[key].startswith("[")):
            out[key] = f"[{', '.join(filter(None, [out[key][1:-1], item.group(1).strip()]))}]"
        elif ":" in line:
            k, v = line.split(":", 1)
            key = k.strip().lower().replace("_", " ").replace("-", " ")
            out[key] = v.strip().strip("\"'")
    return out, body


def skills(front: dict[str, str]) -> list[str] | None:
    """The ``skills:`` list (team skill names: the persona's key tools, named in its wake brief); [] when absent or empty, None when not a list."""
    value = re.sub(r"\s+#.*$", "", front.get("skills", "")).strip()
    if not value:
        return []
    if not (value.startswith("[") and value.endswith("]")):
        return None
    return [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]


def team_skills(repo: Path) -> set[str] | None:
    """Names in the repo's ``skills/team-skills.json`` (a list of ``{name}`` entries, or ``{"skills": [...]}``); None when there is no manifest."""
    path = repo / MANIFEST
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    entries = data.get("skills", []) if isinstance(data, dict) else data
    return {e["name"] for e in entries if isinstance(e, dict) and isinstance(e.get("name"), str)}


def skill_warnings(path: Path, text: str) -> list[str]:
    """Declared skills missing from the team manifest (no manifest, no check)."""
    known = team_skills(repo_root(path))
    declared = skills(frontmatter(text)[0]) or []
    return [] if known is None else [f"persona skill {s!r} is not in {MANIFEST.as_posix()}" for s in declared if s not in known]


def file_errors(path: Path, text: str) -> list[str]:
    front, body = frontmatter(text)
    headings = {m.group(1).strip() for m in re.finditer(r"(?m)^## (.+)$", body)}
    out = [f"persona file missing frontmatter key: {k}" for k in FRONT if not front.get(k)]
    out += [f"persona file has a {k} field: that belongs to the assignment (the epic's Team table), not the persona" for k in sorted(FORBIDDEN & front.keys())]
    out += [f"persona file missing section: ## {s}" for s in BODY if s not in headings]
    out += [f"persona file has a ## {h} section: that belongs to the assignment (the epic's Team table)" for h in sorted(headings) if h.lower() in FORBIDDEN]
    listed = skills(front)
    if listed is None:
        out.append("persona file skills: must be a list of team skill names, e.g. skills: [diagram-design]")
    out += [f"persona skill {s!r} is not a skill name (lowercase, hyphens)" for s in listed or [] if not SKILL.match(s)]
    if front.get("name") and slug(front["name"]) != slug(path.stem):
        out.append(f"persona name {front['name']!r} does not match the file name {path.name}")
    return out


def names(repo: Path) -> dict[str, Path]:
    """Persona files of a repo: slug -> path (``personas/*.md`` at the repo root, README.md aside)."""
    return {slug(p.stem): p for p in sorted((repo / "personas").glob("*.md")) if p.name.lower() != "readme.md"}


def repo_root(path: Path) -> Path:
    here = path.resolve().parent
    return next((p for p in (here, *here.parents) if (p / ".git").exists()), here)


def team(rows: list[dict[str, str]], header: list[str], files: dict | None = None) -> tuple[list[str], list[str]]:
    """(persona slugs, errors) of an epic's ``## Team`` table; with persona files in the repo each persona must have one (the human, Jordi, is no persona)."""
    names = base(header)
    out = [f"Team table missing column: {c}" for c in TEAM_COLUMNS if c not in names]
    people: list[str] = []
    for n, row in enumerate(rows, 1):
        row = {c: row.get(h, "") for c, h in names.items()}
        who = slug(row.get("Persona", ""))
        if not who:
            out.append(f"Team row {n} has no persona")
            continue
        out += [f"Team row {n} ({who}) has empty {c}" for c in TEAM_COLUMNS[1:] if c in names and not row.get(c, "").strip()]
        out += [f"Team lists {who} twice"] * (who in people)
        out += [f"Team persona {who} has no file personas/{who}.md"] * (bool(files) and who not in files and who != HUMAN)
        people.append(who)
    return people, out


def assignee_errors(rows: list[dict[str, str]], people: list[str], files: dict | None = None) -> list[str]:
    """Open (non-draft, unfinished: ``claim.CLOSED``) ledger rows whose assignee is neither a persona on the team (the persona files, else the Team table) nor Jordi."""
    known = set(files or people) | {HUMAN}

    def ok(cell: str) -> bool:  # a claim (claim.py: `<holder> — claimed …, lease until …`) may be held by a persona or a run id
        m = LEASE.search(cell)
        return slug(cell[:m.start()] if m else cell) in known or bool(m and re.fullmatch(r"run_[\w-]+", cell[:m.start()].strip()))
    return [f"ledger row {n} ({r.get('Issue', '')}) is {r['Status']} but assignee {r.get('Owner / Assignment', '')!r} is not a team persona or Jordi"
            for n, r in enumerate(rows, 1) if r.get("Status", "").lower() != "draft" and not CLOSED.match(r.get("Status", "")) and not ok(r.get("Owner / Assignment", ""))]


def epic_errors(path: Path, sections: dict[str, str], header: list[str], rows: list[dict[str, str]], table) -> list[str]:
    """Rules for an epic with a ``## Team`` section (the opt-in; legacy spines are untouched). ``table`` = validate_spine.parse_table."""
    head, cells = table(sections["Team"])
    files = names(repo_root(path))
    people, out = team([dict(zip(head, c)) for c in cells], head, files)
    return out + (assignee_errors(rows, people, files) if "Owner / Assignment" in header and "Status" in header else [])


def team_json(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = [{c: r.get(h, "") for c, h in base(list(r)).items()} for r in rows]
    return [{"persona": slug(r.get("Persona", "")), "cadence": r.get("Cadence", ""), "write_scope": r.get("Write scope", ""), "notes": r.get("Notes", "")} for r in rows]


def roster(repo: Path, nodes: list[dict], ledgers: dict[str, list[dict[str, str]]]) -> list[dict]:
    """Personas (files, then Team rows; Jordi when he has rows), each with its ``skills`` (from the file, else []), ``epics`` and ``queue``: its open ledger rows across the tree (a draft or finished row is nobody's queue)."""
    out = {}
    for k, f in names(repo).items():
        front = frontmatter(f.read_text())[0]
        out[k] = {"name": k, "path": os.path.relpath(f, repo), **front, "skills": skills(front) or [], "epics": [], "queue": []}
    for n in nodes:
        for t in n["team"]:
            out.setdefault(t["persona"], {"name": "Jordi" if t["persona"] == HUMAN else t["persona"], "path": None, "skills": [], "epics": [], "queue": []})["epics"].append(n["path"])
    for epic, rows in ledgers.items():
        for r in rows:
            who = slug(r.get("Owner / Assignment", ""))
            if r.get("Status", "").lower() in OPEN and (who in out or who == HUMAN):
                out.setdefault(who, {"name": "Jordi", "path": None, "skills": [], "epics": [], "queue": []})["queue"].append({"epic": epic, "issue": r.get("Issue", ""), "title": r.get("Title", ""), "status": r.get("Status", "")})
    return list(out.values())


if __name__ == "__main__":
    found = [(p, e) for p in sys.argv[1:] for e in file_errors(Path(p), Path(p).read_text())]
    warned = [(p, w) for p in sys.argv[1:] for w in skill_warnings(Path(p), Path(p).read_text())]
    print(*(f"{p}: {e}" for p, e in found), *(f"{p}: warning: {w}" for p, w in warned), sep="\n")
    sys.exit(int(bool(found)))
