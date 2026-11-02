#!/usr/bin/env python3
"""Shared tree library: heat with a half-life, stable node ids, and a "Recent changes" rollup (references/tree-library.md).

The same three concepts run in two places, and each keeps its own code: this module (spines.py ranks open goals
by heat) and Zenod's TypeScript memory tree (packages/core/src/engine/treeDiscover.ts, heat since EPIC-9 E9-2g;
ids and Recent changes from E9-5b/E9-5c). Nothing imports the other: the algorithm is the contract, written down in
references/tree-library.md, and `assets/tree-library-parity.json` holds inputs with expected outputs that
both sides can test against. Change a constant or a rule here and there in the same breath, or the trees drift.

Pure stdlib, no I/O except `spine_activity` (one `git log` per repo). Dates are `YYYY-MM-DD` day strings, UTC.
"""

from __future__ import annotations

import datetime
import hashlib
import math
import re
import subprocess
from pathlib import Path
from typing import Iterable, Mapping, Sequence

HALF_LIFE_DAYS = 14
HORIZON_DAYS = 120  # events older than this add nothing (0.5 ** (120 / 14) ≈ 0.003 anyway)
MATCH_THRESHOLD = 0.5  # Jaccard overlap of member sets at which a re-derived node keeps an old id
RECENT_CHANGES_KEEP = 20
DATE = re.compile(r"\b(20\d\d-[01]\d-[0-3]\d)\b")


def days_between(earlier: str, later: str) -> int:
    """Whole days from `earlier` to `later` (negative when `earlier` is after `later`)."""
    return (datetime.date.fromisoformat(later) - datetime.date.fromisoformat(earlier)).days


def round3(x: float) -> float:
    """Round half up to 3 decimals, as JavaScript's `Math.round(x * 1000) / 1000` does (Python's round() is half-even)."""
    return math.floor(x * 1000 + 0.5) / 1000


def heat(events: Iterable[str | tuple[str, float]], today: str, half_life: float = HALF_LIFE_DAYS, horizon: int = HORIZON_DAYS) -> float:
    """Sum of weight * 0.5 ** (age / half_life) over dated events, rounded to 3 decimals.

    An event is a day string (weight 1) or `(day, weight)`; weight is the share of the event this node holds
    (Zenod: a capture filed on two topics gives each a share). Future events (age < 0) and events older than
    `horizon` days add nothing. One event today is 1.0; 14 days old 0.5; 28 days old 0.25."""
    total = 0.0
    for event in events:
        day, weight = (event, 1.0) if isinstance(event, str) else event
        age = days_between(day, today)
        if 0 <= age <= horizon and weight:
            total += weight * 0.5 ** (age / half_life)
    return round3(total)


def jaccard(a: Iterable, b: Iterable) -> float:
    """|a ∩ b| / |a ∪ b|; 0.0 for two empty sets."""
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def new_id(members: Iterable, prefix: str = "n-") -> str:
    """Deterministic id for a node no old node matched: `n-` + the first 8 hex of sha1 over its sorted members joined by newlines."""
    return prefix + hashlib.sha1("\n".join(sorted(str(m) for m in members)).encode()).hexdigest()[:8]


def match_ids(previous: Mapping[str, Iterable], current: Sequence[Iterable], threshold: float = MATCH_THRESHOLD) -> list[str]:
    """An id for each current member set: the old id it overlaps most (Jaccard ≥ threshold), one-to-one, else a new id.

    Greedy best-first: all (old, new) pairs at or above the threshold, highest overlap first; ties by old id, then by
    the current index; a pair is taken when neither side is taken yet. (At ≥ 0.5 a set can overlap that much with few
    others, so greedy agrees with an optimal assignment in practice and stays easy to port.) Unmatched sets get
    `new_id(members)`; if that id is already used, `-2`, `-3`, ... is appended."""
    prev = {pid: set(m) for pid, m in previous.items()}
    cur = [set(m) for m in current]
    pairs = sorted(((jaccard(prev[pid], members), pid, i) for pid in prev for i, members in enumerate(cur)), key=lambda p: (-p[0], p[1], p[2]))
    ids: list[str | None] = [None] * len(cur)
    taken: set[str] = set()
    for score, pid, i in pairs:
        if score < threshold:
            break
        if ids[i] is None and pid not in taken:
            ids[i] = pid
            taken.add(pid)
    used = set(prev) | taken
    for i, members in enumerate(cur):
        if ids[i] is None:
            base = candidate = new_id(members)
            n = 1
            while candidate in used:
                n += 1
                candidate = f"{base}-{n}"
            ids[i] = candidate
            used.add(candidate)
    return [i for i in ids if i is not None]


def recent_changes(previous: Mapping[str, Mapping], current: Mapping[str, Mapping]) -> list[dict]:
    """What changed between two derivations keyed by stable id. A node is `{"name": str, "members": [...], "kind": str?}`.

    Ops, in this order, each list sorted by id: `added`, `retired`, `renamed` (from, to), `moved` (kind from, to: e.g.
    working → long-term), `regrouped` (gained, lost member counts). A node may appear under several ops."""
    out: list[dict] = []
    for nid in sorted(set(current) - set(previous)):
        out.append({"op": "added", "id": nid, "name": current[nid]["name"]})
    for nid in sorted(set(previous) - set(current)):
        out.append({"op": "retired", "id": nid, "name": previous[nid]["name"]})
    both = sorted(set(previous) & set(current))
    for nid in both:
        if previous[nid]["name"] != current[nid]["name"]:
            out.append({"op": "renamed", "id": nid, "name": current[nid]["name"], "from": previous[nid]["name"], "to": current[nid]["name"]})
    for nid in both:
        if previous[nid].get("kind") != current[nid].get("kind"):
            out.append({"op": "moved", "id": nid, "name": current[nid]["name"], "from": previous[nid].get("kind"), "to": current[nid].get("kind")})
    for nid in both:
        old, new = set(previous[nid].get("members", ())), set(current[nid].get("members", ()))
        if old != new:
            out.append({"op": "regrouped", "id": nid, "name": current[nid]["name"], "gained": len(new - old), "lost": len(old - new)})
    return out


def change_line(change: Mapping, day: str) -> str:
    """One Markdown bullet: `- 2026-11-02 · renamed House → Housing`."""
    op, name = change["op"], change["name"]
    text = {"added": f"new {name}", "retired": f"retired {name}", "renamed": f"renamed {change.get('from')} → {change.get('to')}",
            "moved": f"moved {name}: {change.get('from')} → {change.get('to')}",
            "regrouped": f"regrouped {name} (+{change.get('gained', 0)} −{change.get('lost', 0)})"}.get(op, f"{op} {name}")
    return f"- {day} · {text}"


def rollup_recent(existing: Sequence[str], changes: Sequence[Mapping], day: str, keep: int = RECENT_CHANGES_KEEP) -> list[str]:
    """The `## Recent changes` bullets after one run: this run's lines first, then the older ones, at most `keep`.
    No changes (the NOOP default) returns `existing` unchanged, trimmed to `keep`."""
    return ([change_line(c, day) for c in changes] + [line for line in existing if line.strip()])[:keep]


def _dates(text: str, today: str) -> set[str]:
    """ISO dates in `text` that are real days, not after `today`."""
    out: set[str] = set()
    for d in DATE.findall(text or ""):
        try:
            out |= {d} if days_between(d, today) >= 0 else set()
        except ValueError:
            pass
    return out


def ledger_days(section: str, today: str) -> set[str]:
    """One activity day per Issue Ledger row: the latest date written in the row (Last Verified, evidence, notes), if any."""
    out: set[str] = set()
    for line in (section or "").splitlines():
        if line.lstrip().startswith("|") and (days := _dates(line, today)):
            out.add(max(days))
    return out


def commit_days(repo: Path, paths: Sequence[str], today: str, horizon: int = HORIZON_DAYS) -> dict[str, set[str]]:
    """Distinct commit days (committer date) per path within the horizon: one `git log` for all paths.
    A git failure or timeout yields no days (the heat is then what the text says), never an error."""
    out: dict[str, set[str]] = {p: set() for p in paths}
    if not paths:
        return out
    since = (datetime.date.fromisoformat(today) - datetime.timedelta(days=horizon)).isoformat()
    try:
        r = subprocess.run(["git", "-c", "core.quotePath=false", "log", f"--since={since}", "--format=\x01%cs", "--name-only", "--relative", "--", *paths],
                           cwd=repo, capture_output=True, text=True, timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return out
    day = None
    for line in r.stdout.splitlines():
        if line.startswith("\x01"):
            day = line[1:].strip()
        elif line.strip() in out and day:
            out[line.strip()].add(day)
    return out


def spine_activity(repo: Path, spines: Mapping[str, Mapping[str, str]], today: str | None = None) -> dict[str, dict]:
    """Heat of each spine from its real activity, keyed by repo-relative path.

    `spines` maps path → its sections (`{"Current State": ..., "Issue Ledger": ...}`). Three sources, each counted as
    distinct days so a burst of commits on one day weighs like one active day per source:
    commits touching the file; dates in Current State `Last attempted:` (which keeps the "before: ..." history);
    and one day per Issue Ledger row (its latest date). Heat = sum over the sources of `heat(days)`.
    Returns `{path: {"heat": float, "last_activity": day | None}}`."""
    today = today or datetime.date.today().isoformat()
    commits = commit_days(repo, list(spines), today)
    out: dict[str, dict] = {}
    for path, sections in spines.items():
        attempted = re.search(r"(?mi)^\s*[-*]?\s*Last attempted:\s*(.*)$", sections.get("Current State", "") or "")
        sources = [commits.get(path, set()), _dates(attempted.group(1) if attempted else "", today), ledger_days(sections.get("Issue Ledger", ""), today)]
        days = set().union(*sources)
        out[path] = {"heat": round3(sum(heat(s, today) for s in sources)), "last_activity": max(days) if days else None}
    return out


def rank(paths: Sequence[str], heats: Mapping[str, float]) -> list[str]:
    """Hottest first; equal heat keeps the given (tree) order."""
    return [p for _, p in sorted(enumerate(paths), key=lambda ip: (-heats.get(ip[1], 0.0), ip[0]))] if paths else []
