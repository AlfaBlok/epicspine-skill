#!/usr/bin/env python3
"""Draw EpicTeam's feature list into its public page (agent_team E43-S7 round 2).

The list has one source: agent_team docs/features/epicteam.json, which the console also shows (/deck/all#features).
This writes its groups into team/index.html between the features:team markers: a group's features that already have
their own section on the page (`section`) are left to it, the others are listed under the group's title. Public
words only: a title or text that carries a row code, a file path or brackets is refused.

Usage: feature_list.py --repo agent_team=~/github/agent_team [--check]
       (--check: exit 1 when the page differs from what the list gives, and write nothing)
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
LISTS = {"team": {"page": "team/index.html", "repo": "agent_team", "file": "docs/features/epicteam.json"}}
PRIVATE = re.compile(r"\b(E\d+-[A-Z]?\d+|EPIC-\d+|L-\d+)\b|[/;()]")


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def render(data: dict) -> str:
    out = []
    for g in data.get("groups", []):
        items = [f for f in g.get("features", []) if not f.get("section")]
        if not items:
            continue
        for f in items:
            for k in ("title", "text"):
                if PRIVATE.search(f.get(k, "")):
                    raise SystemExit(f"{f.get('id')}: its {k} is not public words: {f.get(k)!r}")
        gid = slug(g["id"])
        title = g["title"].rstrip(".") + "."
        lis = "\n".join(f'        <li><h3>{esc(f["title"])}</h3><p>{esc(f["text"])}</p></li>' for f in items)
        intro = f'\n        <p class="was">{esc(g["intro"])}</p>' if g.get("intro") else ""
        out.append(
            f'  <section class="band" id="{gid}" aria-labelledby="h-{gid}">\n'
            f'    <div class="container nice">\n'
            f'      <div class="say">\n'
            f'        <h2 id="h-{gid}">{esc(title)}</h2>{intro}\n'
            f'      </div>\n'
            f'      <ul class="nice-list">\n{lis}\n      </ul>\n'
            f'    </div>\n'
            f'  </section>'
        )
    return "\n".join(out)


def splice(text: str, name: str, block: str) -> str:
    begin, end = f"<!-- features:{name} begin (tools/feature_list.py writes this) -->", f"<!-- features:{name} end -->"
    i, j = text.find(begin), text.find(end)
    if i < 0 or j < i:
        raise SystemExit(f"{name}: the page has no features:{name} markers")
    return text[:i + len(begin)] + "\n" + block + "\n" + text[j:]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", action="append", default=[], help="name=path of a repo checkout")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    repos = dict(r.split("=", 1) for r in a.repo)
    differ = 0
    for name, spec in LISTS.items():
        if spec["repo"] not in repos:
            raise SystemExit(f"--repo {spec['repo']}=<checkout> is needed for {name}")
        data = json.loads((Path(repos[spec["repo"]]).expanduser() / spec["file"]).read_text(encoding="utf-8"))
        page = SITE / spec["page"]
        old = page.read_text(encoding="utf-8")
        new = splice(old, name, render(data))
        if new == old:
            continue
        differ += 1
        if a.check:
            print(f"{spec['page']}: differs from {spec['repo']} {spec['file']}")
        else:
            page.write_text(new, encoding="utf-8")
            print(f"{spec['page']}: written from {spec['repo']} {spec['file']}")
    return 1 if a.check and differ else 0


if __name__ == "__main__":
    sys.exit(main())
