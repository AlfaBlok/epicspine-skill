"""The content checks a pack's `checks` name, run on one row at the transitions it passed (pack_validate.py).

link_rule (max links, none on line n), disclosure (a phrase in the first lines), never_say (the brief's list),
hold_rules (a quoted phrase, or `field: value`, from the brief's hold table: matched means held, not scheduled), caps
(per platform: posts a day, posts per community a week, replies a day, counting rows in the live states), link_present."""
from __future__ import annotations

import datetime as dt
import re

URL = re.compile(r"https?://\S+")
BREAK = re.compile(r"<br\s*/?>|\\n|\n", re.I)


def lines(rec: dict) -> list[str]:
    return [x.strip() for x in BREAK.split(rec.get("text", "")) if x.strip()]


def day(rec: dict) -> str:
    return (rec.get("slot") or rec.get("date") or "")[:10]


def phrases(entry: str) -> list[str]:
    """Never-say phrases in one list item: its quoted parts, else the item itself."""
    quoted = re.findall(r'["“]([^"”]+)["”]', entry)
    return quoted or [entry.strip().rstrip(".").strip("`*")] if entry.strip().lower() not in ("none", "") else []


def holds(rule: str, rec: dict) -> bool:
    """A hold rule matches on a quoted phrase in title/text, or `field: value` (Platform: Reddit); free text is the Writer's call."""
    hay = f"{rec.get('title', '')} {rec.get('text', '')}".lower()
    quoted = re.findall(r'["“]([^"”]+)["”]', rule)
    if quoted:
        return any(q.lower() in hay for q in quoted)
    m = re.fullmatch(r"\s*([\w ]+?)\s*[:=]\s*(.+?)\s*", rule)
    return bool(m and m.group(1).lower() in rec and rec[m.group(1).lower()].lower() == m.group(2).lower())


def run_check(key: str, c: dict, rec: dict, ctx: dict) -> list[str]:
    p, text = c.get("params", {}), lines(rec)
    if key == "link_rule":
        out, links = [], URL.findall(rec.get("text", ""))
        if len(links) > p.get("max_links", len(links)):
            out.append(f"{len(links)} links in the text (max {p['max_links']})")
        n = p.get("no_link_on_line")
        return out + ([f"a link on line {n}"] if n and len(text) >= n and URL.search(text[n - 1]) else [])
    if key == "disclosure":
        head = " ".join(text[:p.get("within_lines", 2)]).lower().replace("’", "'")
        return [] if any(x.lower() in head for x in p.get("phrases", [])) else [
            f"no disclosure in the first {p.get('within_lines', 2)} lines (say one of: {', '.join(p.get('phrases', []))})"]
    if key == "never_say":
        hay = f"{rec.get('title', '')} {rec.get('text', '')}".lower()
        return [f"says never-say phrase {x!r}" for e in ctx["source"](c["source"]) for x in phrases(e) if x and x.lower() in hay]
    if key == "hold_rules":
        return [f"matches hold rule {r.get('id') or r.get('match')} ({r.get('match')}): it goes to held, not scheduled"
                for r in ctx["source"](c["source"]) if r.get("match") and holds(r["match"], rec)]
    if key == "link_present":
        return [] if URL.match(rec.get(p.get("field", "link"), "")) else ["posted without its link (add it in the same commit)"]
    if key == "caps":
        plat, kind, out = rec.get("platform", "").lower(), rec.get("kind", "").lower(), []
        live = [r for r in ctx["rows"] if r.get(ctx["status"], "").lower() in ctx["live"] and r.get("platform", "").lower() == plat]
        posts = [r for r in live if r.get("kind", "").lower() == "post"]
        if kind == "post" and len(n := [r for r in posts if day(r) == day(rec)]) > p.get("threads_per_day", 1e9):
            out.append(f"{len(n)} posts on {rec.get('platform')} on {day(rec)} (cap {p['threads_per_day']} a day)")
        try:
            week = dt.date.fromisoformat(day(rec)).isocalendar()[:2]
            same = [r for r in posts if r.get("community") and r.get("community") == rec.get("community")
                    and day(r) and dt.date.fromisoformat(day(r)).isocalendar()[:2] == week]
        except ValueError:
            same = []
        if kind == "post" and len(same) > p.get("per_community_per_week", 1e9):
            out.append(f"{len(same)} posts in {rec.get('community')} that week (cap {p['per_community_per_week']} a week)")
        if kind != "post" and len(n := [r for r in live if r.get("kind", "").lower() != "post" and day(r) == day(rec)]) > p.get("replies_per_day", 1e9):
            out.append(f"{len(n)} replies on {rec.get('platform')} on {day(rec)} (cap {p['replies_per_day']} a day)")
        return out
    return []
