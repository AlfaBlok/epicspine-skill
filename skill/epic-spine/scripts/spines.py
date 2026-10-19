#!/usr/bin/env python3
"""The epic log: one tree of goals per repo, hung from the root spine (references/spine-model.md).

``spines.py [--json | --active] --repo DIR`` finds the root (AGENTS.md ``Root spine:``, else a root-typed header), walks children
(a child's ``Parent spine:`` header decides; the parent's Spine Map must agree; links resolve against the file's folder, else
the repo root) and lists goal docs outside the tree as orphans. Goal doc = a ``Spine ID:`` line or an E<n>-*/EPIC*/*SPINE*/*PLAN*
name; skipped: archive/, node_modules, dot-dirs, handoffs/, examples/, fixtures/, test/, tests/, vendored skills. Exits 0."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_spine as v  # noqa: E402
from epic_log import active, link_problems, render, rollup, stale  # noqa: E402

SKIP = {"archive", "node_modules", "vendor", "wt", "worktrees", "handoffs", "examples", "fixtures", "test", "tests", "__pycache__"}
NAMED = re.compile(r"(?i)^(e\d+[-_]|epic)|(^|[-_ ])(spine|plan)($|[-_ 0-9])")
ID_LINE = re.compile(r"(?m)^Spine ID:")
ROOT_LINE = re.compile(r"Root spine: \[?`?([^`\]\s)]+)")
DONE = re.compile(rf"- \[([ xX])\] ({v.ID})[ \t]*(.*)")


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def is_goal(repo: Path, rel: Path, text: str) -> bool:
    dirs = rel.parts[:-1]
    skipped = any(d in SKIP or d.startswith(".") for d in dirs) or any((repo.joinpath(*dirs[:i]) / "SKILL.md").is_file() for i in range(len(dirs) + 1))
    return rel.suffix == ".md" and not skipped and bool(NAMED.search(rel.stem) or ID_LINE.search(text))


def goal_docs(repo: Path) -> list[Path]:
    found = []
    for top, dirs, files in os.walk(repo):
        vendored = "SKILL.md" in files
        dirs[:] = [] if vendored else sorted(d for d in dirs if d not in SKIP and not d.startswith("."))
        if not vendored:
            found += [p for p in (Path(top, n) for n in sorted(files)) if p.suffix == ".md" and (NAMED.search(p.stem) or ID_LINE.search(read(p)))]
    return found


def link(path: Path, value: str, cache: dict) -> Path | None:
    """A header/map link target: relative to the file's folder, else to the repo root (cache[None])."""
    target = v.resolve_local_link(path, value)
    alt = v.resolve_local_link(cache[None] / "-", value) if target and not target.exists() else None
    return alt if alt and alt.exists() else target


def meta(path: Path, cache: dict) -> dict | None:
    path = path.resolve()
    if path not in cache:
        text = read(path) if path.is_file() else None
        fields, sections = v.parse_fields(text or ""), v.parse_sections(text or "")
        rows = [(r.get("Spine ID", ""), link(path, r.get("Spine", ""), cache)) for r in v.table_rows(sections.get("Spine Map", ""))]
        cache[path] = None if text is None else {"path": path, "text": text, "fields": fields, "sections": sections, "id": fields.get("Spine ID", ""),
                                                  "parent": link(path, fields.get("Parent spine", ""), cache), "rows": rows}
    return cache[path]


def find_root(repo: Path, cache: dict, docs: list[Path] | None = None) -> Path | None:
    repo = cache.setdefault(None, repo.resolve())
    declared = ROOT_LINE.search(read(repo / "AGENTS.md"))
    if declared:
        return next((p.resolve() for p in [repo / declared.group(1).rstrip(".")] if p.is_file()), None)
    roots = (p for p in docs or goal_docs(repo) if (f := meta(p, cache)["fields"]).get("Spine Type", "").lower() == "root" or f.get("Root spine", "").lower() == "self")
    return next((p.resolve() for p in roots), None)


def parent_file(path: Path, cache: dict) -> Path | None:
    m = meta(path, cache)
    return m["parent"] if m and m["parent"] and meta(m["parent"], cache) else None


def problems(repo: Path, path: Path, cache: dict) -> list[str] | None:
    """Why ``path`` is not a consistent node of the tree (None: the repo has no root spine). Walks up one chain only."""
    root = find_root(repo, cache)
    if root is None:
        return None
    out, cur, seen = [], path.resolve(), set()
    while cur != root:
        m = meta(cur, cache)
        parent = parent_file(cur, cache)
        if not m["id"]:
            return out + [f"{cur.name}: no Spine ID header"]
        if parent is None or cur in seen:
            return out + [f"{cur.name}: Parent spine missing or not a file, so not reachable from the root"]
        out += [f"{cur.name}: {p}" for p in link_problems(m, meta(parent, cache))]
        seen.add(cur)
        cur = parent
    return out


def scan(repo: Path) -> dict:
    cache = {None: (repo := repo.resolve())}
    docs = [p.resolve() for p in goal_docs(repo)]
    root = find_root(repo, cache, docs)
    rel = lambda p: os.path.relpath(p, repo)  # noqa: E731
    header_kids: dict[Path, list[Path]] = {}
    for d in docs:
        if parent_file(d, cache):
            header_kids.setdefault(meta(d, cache)["parent"], []).append(d)
    nodes: dict[str, dict] = {}
    mismatches: list[dict] = []
    title = lambda m, fallback: re.sub(r"^(EPIC|SPINE):\s*", "", t.group(1)) if (t := re.search(r"(?m)^# (.+)", m["text"])) else fallback  # noqa: E731

    def visit(path: Path) -> str:
        m = meta(path, cache)
        state = v.read_state(m["text"])[0].get("status", "")
        status = m_.group() if (m_ := re.match(r"[a-z]+", state.lower())) else ""
        dod = [{"id": x.group(2), "text": x.group(3), "done": x.group(1) != " "} for _, line in v.criteria(m["text"], ("Definition Of Done",)) if (x := DONE.match(line.strip()))]
        node = nodes[rel(path)] = {"id": m["id"], "path": rel(path), "title": title(m, path.stem), "parent": rel(m["parent"]) if parent_file(path, cache) else None,
                                   "type": m["fields"].get("Spine Type", "").lower() or ("root" if path == root else ""),
                                   "status": status, "rollup_status": status, "dod": dod, "children": [],
                                   "superseded_by": rel(sup) if (sup := link(path, m["fields"].get("Superseded by", ""), cache)) else None}
        kids = list(header_kids.get(path, []))
        for _, target in m["rows"]:
            tm = meta(target, cache) if target else None
            other = parent_file(target, cache) if tm else None
            if tm is None:
                mismatches.append({"path": rel(path), "parent": None, "problem": "Spine Map row points at a missing file"})
            elif other not in (None, path):
                mismatches.append({"path": rel(target), "parent": rel(path), "problem": f"listed in this Spine Map but its Parent spine is {rel(other)}"})
            elif target not in kids:
                kids.append(target)
        for kid in kids:
            if rel(kid) not in nodes:
                nodes[rel(kid)] = {}  # reserve: guards cycles
                visit(kid)
                node["children"].append(rel(kid))
                mismatches.extend({"path": rel(kid), "parent": rel(path), "problem": p} for p in link_problems(meta(kid, cache), m))
        node["rollup_status"] = rollup(status, [nodes[c]["rollup_status"] for c in node["children"]], dod) if node["children"] or dod else status
        return node["rollup_status"]

    if root:
        visit(root)
    queue = [d for d in docs if rel(d) not in nodes]
    for d in queue:  # docs a goal links as children are goal docs too
        queue += [t for _, t in meta(d, cache)["rows"] if t and t.suffix == ".md" and t.is_file() and rel(t) not in nodes and t not in queue]
    orphans = [{"path": rel(d), "title": title(meta(d, cache), d.stem), "reason": "not reachable from the root" if meta(d, cache)["id"] else "no Spine ID header"} for d in queue]
    return {"root": rel(root) if root else None, "nodes": list(nodes.values()), "orphans": orphans, "mismatches": mismatches,
            "stale": stale(repo, list(nodes.values()))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--active", action="store_true", help="list open goals, one line each (stale marked)")
    args = parser.parse_args()
    log = scan(Path(args.repo))
    print(json.dumps(log, indent=2) if args.json else active(log) if args.active else render(log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
