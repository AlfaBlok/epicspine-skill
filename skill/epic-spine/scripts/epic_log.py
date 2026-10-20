#!/usr/bin/env python3
"""Epic log helpers for spines.py / spine_new.py / session_sync.py: rollup, text views, next code, stale goals."""

from __future__ import annotations

import datetime
import os
import re
import subprocess
import time
from pathlib import Path

import validate_spine as v

OPEN = ("draft", "ready", "active", "blocked")
CODE = re.compile(r"^(?:EPIC[- ]?|E)(\d+)\b")
STALE_DAYS = 14
STALE_ASK_DAYS = 7
ASK = re.compile(r"-\s+\[(?:ask:\s*(decide|approve|provide)\s+@(\S+)\s+since\s+(\d{4}-\d\d-\d\d)(?:\s+row\s+(\S+))?|answered\s+\d{4}-\d\d-\d\d\s+@(\S+))\]\s*(.*)")
ASK_FIELD = re.compile(r"(options|recommend|context|answer):\s*(.*)", re.S)


def next_code(titles: list[str]) -> int:
    """Highest EPIC-<n> / `E4 ...` / `EPIC 0 ...` title code plus one."""
    return 1 + max((int(m.group(1)) for t in titles if (m := CODE.match(t.strip()))), default=0)


def rollup(own: str, kids: list[str], dod: list[dict]) -> str:
    """Derived: blocked wins; all children and criteria done: done; any progress: active; else the own status."""
    parts = kids + ["done" if d["done"] else "open" for d in dod]
    if own == "blocked" or "blocked" in kids:
        return "blocked"
    if parts and all(p == "done" for p in parts):
        return "done"
    return "active" if own == "active" or "active" in parts or "done" in parts else own or "draft"


def link_problems(child: dict, parent: dict) -> list[str]:
    """The child's header and the parent's Spine Map must agree."""
    rows = [i for i, t in parent["rows"] if t == child["path"]]
    return (["Parent spine header does not name " + parent["path"].name] if child["parent"] != parent["path"] else []) + \
        ([] if child["id"] in rows else ["Spine Map Spine ID differs"] if rows else ["not in the parent's Spine Map"])


def stale(repo: Path, nodes: list[dict], now: float | None = None) -> list[dict]:
    """Active/blocked goals whose file's last commit is 14+ days old (one git call each; untracked files are skipped)."""
    out, now = [], now or time.time()
    for n in nodes:
        if n["status"] in ("active", "blocked"):
            r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", n["path"]], cwd=repo, capture_output=True, text=True, timeout=5)
            if r.stdout.strip().isdigit() and (days := int((now - int(r.stdout)) // 86400)) >= STALE_DAYS:
                out.append({"path": n["path"], "title": n["title"], "days": days})
    return out


def active(log: dict) -> str:
    """One line per open goal: `<title> — <status> — <path>` (+ stale mark)."""
    days = {s["path"]: s["days"] for s in log["stale"]}
    return "\n".join(f"{n['title']} — {n['status']} — {n['path']}" + (f" — STALE {days[n['path']]}d" if n["path"] in days else "")
                     for n in log["nodes"] if n["status"] in OPEN)


def attention(repo: Path) -> str:
    """The background-sync line for stale goals ('' when none, no root spine, or on any error)."""
    try:
        import spines
        if spines.find_root(repo, {}) is None:
            return ""
        n = len(spines.scan(repo)["stale"])
        return f"{repo.name}: {n} goals active but untouched {STALE_DAYS}+ days (spines.py --active)" if n else ""
    except Exception:
        return ""


def render(log: dict) -> str:
    by_path = {n["path"]: n for n in log["nodes"]}
    lines: list[str] = []

    def show(path: str, depth: int) -> None:
        n, pad = by_path[path], "  " * depth
        lines.append(f"{pad}- {n['title']} ({n['path']}) {n['status'] or '?'}" + (f" -> {n['rollup_status']}" if n["rollup_status"] != n["status"] else ""))
        lines.extend(f"{pad}  [{'x' if d['done'] else ' '}] {d['id']} {d['text']}" for d in n["dod"])
        for child in n["children"]:
            show(child, depth + 1)

    if log["root"]:
        show(log["root"], 0)
    else:
        lines.append("no root spine (Root spine: none): nothing is in the tree")
    lines += [f"orphan: {o['path']} ({o['reason']})" for o in log["orphans"]]
    lines += [f"mismatch: {m['path']}: {m['problem']}" for m in log["mismatches"]]
    return "\n".join(lines)


def asks(text: str, path: Path, repo: Path) -> list[dict]:
    """``## Waiting on`` ask lines in the docs/doctrine/human-asks.md shape; ``context`` is repo-relative when local (else kept as-is)."""
    out = []
    for line in v.parse_sections(text).get("Waiting on", "").splitlines():
        if not (m := ASK.fullmatch(line.strip())):
            continue
        kind, who, since, row, answered_by, rest = m.groups()
        question, *parts = re.split(r"\s+[—–]\s+", rest.strip())
        fields: dict[str, str] = {}
        for part in parts:
            f = ASK_FIELD.fullmatch(part.strip())
            if f:
                fields[last := f.group(1)] = f.group(2).strip()
            elif fields:  # a dash inside the previous field's text
                fields[last] += " — " + part
            else:
                question += " — " + part
        options = [o.strip() for o in fields.get("options", "").split("|") if o.strip()]
        out.append({"who": who or answered_by, "ask": kind, "question": question, "options": options, "recommend": fields.get("recommend") or None,
                    "context": ask_context(fields.get("context", ""), path, repo), "since": since, "row": row,
                    "state": "open" if kind else "answered", "answer": fields.get("answer") or None})
    return out


def ask_context(value: str, path: Path, repo: Path) -> str | None:
    """A markdown link or bare path/URL: external kept as-is, local made repo-relative (the file's folder first, else the repo root)."""
    target = (m.group(1) if (m := re.fullmatch(r"\[[^\]]*\]\(([^)]+)\)", value.strip())) else value.strip()).strip("<>")
    if not target or "://" in target or target.startswith("mailto:"):
        return target or None
    name, _, frag = target.partition("#")
    here = (path.parent / name).resolve() if name else path.resolve()
    found = here if here.exists() or not (repo / name).exists() else (repo / name).resolve()
    return (os.path.relpath(found, repo) if found.is_relative_to(repo) else target) + (f"#{frag}" if frag else "")


def ask_issues(text: str, today: datetime.date | None = None) -> list[str]:
    """Advisory (never blocking): blocked rows/epic no open ask names, open asks missing a required field, open asks over 7 days old."""
    today, issues = today or datetime.date.today(), []
    found = [a for a in asks(text, Path("-"), Path("-")) if a["state"] == "open"]
    key = lambda k: k.lower().strip("#[] ").rstrip(".:)")  # noqa: E731
    named = {key(a["row"]) for a in found if a["row"]}
    sections = v.parse_sections(text)
    header, rows = v.parse_table(sections.get("Issue Ledger", ""))
    for row in (dict(zip(header, r)) for r in rows) if "Status" in header else []:
        if v.normalize(row["Status"]).lower().startswith("blocked"):
            first = (row.get("Title", "").split() or [""])[0].rstrip(".:)")
            keys = {key(k) for k in (first, row.get("Issue", ""), row.get("Ticket", "")) if k.strip()}
            if not keys & named:
                issues.append(f"ledger row '{first or row.get('Issue', '?')}' is blocked but no open ask names it (add one under ## Waiting on, `row <id>`)")
    status = v.parse_key_values(sections.get("Current State", "")).get("Status", "").lower()
    if status.startswith("blocked") and not found:
        issues.append("Status is blocked but no open ask is under ## Waiting on")
    for a in found:
        label = f"ask '{a['question'][:40]}'"
        issues += [f"{label} is missing {n}" for n, ok in (("options", a["ask"] != "decide" or a["options"]), ("recommend", a["ask"] == "provide" or a["recommend"]), ("context", a["context"])) if not ok]
        if (today - datetime.date.fromisoformat(a["since"])).days > STALE_ASK_DAYS:
            issues.append(f"stale ask: {label} to @{a['who']} open since {a['since']}")
    return issues
