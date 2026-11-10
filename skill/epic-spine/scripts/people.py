"""E90-S3 (agent_team EPIC-90, many humans): a world's humans, one line each under ``## People`` in its root spine.

    ## People
    - @Jordi : owner · area: all · alerts: WhatsApp, daily summary 08:00 Mexico City
    - @Marta : expert · area: books, tax filings · alerts: email, browser 09:00 to 18:00 Madrid
    - @Leo : analyst · area: books · escalates to: @Marta after 24 h · alerts: browser
    - @Sofia : made aware · area: tax filings · alerts: weekly email

Roles: owner (final say: goals, people, money), expert (answers and approves inside their area), analyst (answers first,
escalates when unsure), made aware (reads, never blocks). The repo is the roster: every persona and host reads these
names; a console keeps only which login is which handle. No section: one human, the owner, as before.
"""
from __future__ import annotations

import re

import validate_spine as v

FORM = "`- @<handle> : owner|expert|analyst|made aware · area: <goals> · escalates to: @<handle> after <n> h · alerts: <how>`"
LINE = re.compile(r"[-*]\s+@([A-Za-z0-9][\w.-]*)\s*:\s*(.+)")
ROLES = {"owner": "owner", "expert": "expert", "analyst": "analyst", "made aware": "aware", "aware": "aware"}


def parse(text: str) -> tuple[list[dict], list[str]]:
    """The People list of a root spine and the lines the tools cannot read (each naming the form)."""
    people: list[dict] = []
    problems: list[str] = []
    for raw in v.parse_sections(text).get("People", "").splitlines():
        line = raw.strip()
        if not line[:1] in "-*" or not line[1:].strip():
            continue
        m = LINE.fullmatch(line)
        if not m:
            problems.append(f"People line '{line[:50]}' is not a form the tools read: write {FORM}")
            continue
        handle, rest = m.groups()
        role_text, *parts = re.split(r"\s+[·|]\s+", rest)
        role = ROLES.get(role_text.strip().lower())
        if not role:
            problems.append(f"@{handle}: role '{role_text.strip()}' is not one of owner, expert, analyst, made aware")
            continue
        if any(p["handle"].lower() == handle.lower() for p in people):
            problems.append(f"@{handle} is listed twice")
            continue
        p: dict = {"handle": handle, "role": role, "area": [], "escalates_to": None, "escalate_after_hours": None, "alerts": None}
        for part in parts:
            kv = re.fullmatch(r"\s*(area|escalates to|alerts)\s*:\s*(.*)", part, re.I)
            if not kv:
                continue
            key, val = kv.group(1).lower(), kv.group(2).strip()
            if key == "area":
                p["area"] = [a.strip() for a in val.split(",") if a.strip()]
            elif key == "alerts":
                p["alerts"] = val
            elif e := re.search(r"@([A-Za-z0-9][\w.-]*)(?:\s+after\s+(\d+(?:\.\d+)?)\s*(h|hours?|d|days?)\b)?", val, re.I):
                p["escalates_to"] = e.group(1)
                if e.group(2):
                    p["escalate_after_hours"] = float(e.group(2)) * (24 if e.group(3).lower().startswith("d") else 1)
        if role == "owner" and not p["area"]:
            p["area"] = ["all"]
        people.append(p)
    names = {p["handle"].lower() for p in people}
    problems += [f"@{p['handle']} escalates to @{p['escalates_to']}, who is not on the People list" for p in people if p["escalates_to"] and p["escalates_to"].lower() not in names]
    if people and not any(p["role"] == "owner" for p in people):
        problems.append("the People list names no owner")
    return people, problems


def unknown(people: list[dict], nodes: list[dict]) -> list[str]:
    """Open asks naming someone off the People list (who, approve by, aware); nothing when the world lists no People."""
    if not people:
        return []
    names = {p["handle"].lower() for p in people}
    out = []
    for n in nodes:
        for a in (a for a in n.get("waiting_on", []) if a.get("state") == "open"):
            for h in [a.get("who"), a.get("approve_by"), *(a.get("aware") or [])]:
                if h and h.lower() not in names:
                    out.append(f"{n['path']}: ask {a.get('code') or a.get('question', '')[:30]} names @{h}, who is not on the People list")
    return out


def of_root(root_text: str, nodes: list[dict]) -> dict:
    """`spines.py --json` keys: the root spine's People list and its problems (unreadable lines, names off the list)."""
    found, problems = parse(root_text)
    return {"people": found, "people_problems": problems + unknown(found, nodes)}
