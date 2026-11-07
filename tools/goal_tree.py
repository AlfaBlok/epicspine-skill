#!/usr/bin/env python3
"""Draw real goal trees and the voice-note fan-out into the public pages (agent_team E43-S8, E43-S9).

Reads each repo named in tools/goal-trees.json with `spines.py --json` (goals, their status, parents) and the
Issue Ledger of the goals it draws (steps), then writes two inline SVGs per drawing into the page between its
markers: a wide one, root on top and the smaller goals below, and a phone one, the same tree as an outline.
The labels are the public wording of the real titles; statuses and counts come from the repos. A drawing that
carries a private word (the config's "private" list) is refused.

Usage: goal_tree.py --repo skill=. --repo agent_team=~/github/agent_team --repo campaign=~/github/epic-campaign
       [--check]   (exit 1 when a page differs from what the repos give, and write nothing)
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
SCRIPTS = SITE / "skill" / "epic-spine" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import validate_spine  # noqa: E402

STATE = {"done": "done", "review": "review", "held": "review", "active": "active", "blocked": "active",
         "scheduled": "active", "ready": "planned", "draft": "planned", "deferred": "planned"}
STATE_WORD = {"done": "done", "review": "waiting for review", "active": "in progress", "planned": "planned"}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def state_of(word: str) -> str | None:
    w = (word or "").strip().lower().split()[0] if (word or "").strip() else ""
    return STATE.get(w.strip("`*"))


def plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


class Repo:
    def __init__(self, root: Path):
        self.root = root
        out = subprocess.run([sys.executable, str(SCRIPTS / "spines.py"), "--json", "--repo", str(root)],
                             capture_output=True, text=True, check=True).stdout
        data = json.loads(out)
        self.nodes = {n["path"]: n for n in data["nodes"]}
        self._rows: dict[str, list[dict]] = {}

    def rows(self, path: str) -> list[dict]:
        if path not in self._rows:
            sections = validate_spine.parse_sections((self.root / path).read_text(encoding="utf-8"))
            self._rows[path] = validate_spine.table_rows(sections.get("Issue Ledger", ""))
        return self._rows[path]

    def live(self, path: str) -> bool:
        return self.nodes[path]["status"] != "superseded"

    def kids(self, path: str) -> list[str]:
        return [p for p, n in self.nodes.items() if n["parent"] == path and self.live(p)]

    def steps(self, path: str) -> int:
        return sum(1 for r in self.rows(path) if state_of(r.get("Status", "")))

    def below(self, path: str) -> tuple[int, int]:
        """Goals under this one (any depth) and steps in it and them."""
        goals, steps = 0, self.steps(path)
        for k in self.kids(path):
            g, s = self.below(k)
            goals, steps = goals + 1 + g, steps + s
        return goals, steps


# ---- the tree to draw: nodes with level, label, sub, state, children -------------------------------------------

def node(label, level, state=None, sub="", focus=False, more=False, note=""):
    return {"label": label, "level": level, "state": state, "sub": sub, "focus": focus, "more": more, "note": note, "kids": []}


def build(spec: dict, repo: Repo) -> dict:
    rp = spec["root"]["path"]
    goals, steps = repo.below(rp)
    root = node(spec["root"]["label"], 0, None, f"{plural(goals, 'goal', 'goals')} and {plural(steps, 'step', 'steps')} in its repo")
    for c in spec["children"]:
        n = repo.nodes[c["path"]]
        g, s = repo.below(c["path"])
        sub = (f"{plural(g, 'goal', 'goals')} below, " if g else "") + plural(s, "step", "steps")
        kid = node(c["label"], 1, state_of(n["status"]), sub, c.get("focus", False))
        root["kids"].append(kid)
        if "rows" in c:
            rows = repo.rows(c["path"])
            live = [r for r in rows if state_of(r.get("Status", ""))]
            for r in c["rows"]:
                row = rows[r["id"]] if isinstance(r["id"], int) else next(x for x in rows if x.get("Issue") == r["id"])
                step = node(r["label"], 2, state_of(row["Status"]), "", r.get("focus", False), note=r.get("note", ""))
                kid["kids"].append(step)
                if "posts" in r:
                    ids = re.findall(r"P-\d{4}", row.get("Latest Evidence", ""))
                    ledger = validate_spine.table_rows((repo.root / r["posts"]["ledger"]).read_text(encoding="utf-8"))
                    by_id = {p.get("Id"): p for p in ledger}
                    for pid in dict.fromkeys(ids):
                        step["kids"].append(node(r["posts"]["labels"][pid], 3, state_of(by_id[pid]["Status"])))
            rest = len(live) - len(c["rows"])
            if rest > 0:
                kid["kids"].append(node(f"+{plural(rest, 'more step', 'more steps')}", 2, more=True))
    rest = len(repo.kids(rp)) - len(spec["children"])
    if rest > 0:
        root["kids"].append(node(f"+{plural(rest, 'more goal', 'more goals')}", 1, more=True))
    return root


def walk(n: dict):
    yield n
    for k in n["kids"]:
        yield from walk(k)


# ---- text ---------------------------------------------------------------------------------------------------------

def wrap(text: str, size: float, width: float, lines: int = 2) -> list[str]:
    per = max(6, int(width / (size * 0.53)))
    out, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > per:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    out.append(cur)
    if len(out) > lines:
        out = out[:lines - 1] + [" ".join(out[lines - 1:])]
    return out


# level: width, label size, sub size (wide drawing)
WIDE = {0: (360, 22, 14), 1: (184, 16, 13), 2: (176, 15, 13), 3: (176, 14, 13)}
W = 1200
GAP = 16
BAND = 64  # vertical room between levels for the connectors


def box_height(n: dict, width: float, size: float, sub: float) -> tuple[float, list[str]]:
    pad_l = 34 if n["state"] else 16
    lines = wrap(n["label"], size, width - pad_l - 14)
    h = 20 + len(lines) * size * 1.22 + ((sub * 1.3 + 4) if (n["sub"] or n["note"]) else 0)
    return h, lines


def box(n: dict, x: float, y: float, w: float, h: float, lines: list[str], size: float, sub: float) -> str:
    cls = ["gt-box", f"gt-l{n['level']}"]
    if n["more"]:
        cls.append("gt-more")
    if n["focus"]:
        cls.append("gt-focus")
    out = [f'<g class="{" ".join(cls)}">', f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="2"/>']
    tx = x + (34 if n["state"] else 16)
    if n["state"]:
        out.append(f'<circle class="gt-dot gt-{n["state"]}" cx="{x + 18:.0f}" cy="{y + 10 + size * 0.62:.1f}" r="5"><title>{esc(STATE_WORD[n["state"]])}</title></circle>')
    ty = y + 10 + size
    for line in lines:
        out.append(f'<text class="gt-name" x="{tx:.0f}" y="{ty:.1f}" font-size="{size}">{esc(line)}</text>')
        ty += size * 1.22
    extra = n["note"] or n["sub"]
    if extra:
        out.append(f'<text class="gt-sub{" gt-note" if n["note"] else ""}" x="{tx:.0f}" y="{ty + 3:.1f}" font-size="{sub}">{esc(extra)}</text>')
    out.append("</g>")
    return "".join(out)


def wide(tree: dict, slug: str, title: str, desc: str) -> str:
    levels: dict[int, list[dict]] = {}
    for n in walk(tree):
        levels.setdefault(n["level"], []).append(n)
    geo: dict[int, tuple] = {}
    y = 8
    for lv in sorted(levels):
        w, size, sub = WIDE[lv]
        hs = [box_height(n, w, size, sub) for n in levels[lv]]
        h = max(x[0] for x in hs)
        for n, (_, lines) in zip(levels[lv], hs):
            n["_lines"] = lines
        geo[lv] = (y, h)
        y += h + BAND
    height = y - BAND + 8
    # x: each family of children centred under its parent, kept inside the frame
    tree["_x"] = (W - WIDE[0][0]) / 2
    parts_lines, parts_boxes = [], []
    for n in walk(tree):
        if not n["kids"]:
            continue
        lv = n["level"] + 1
        w = WIDE[lv][0]
        k = len(n["kids"])
        total = k * w + (k - 1) * GAP
        pcx = n["_x"] + WIDE[n["level"]][0] / 2
        start = min(max(8, pcx - total / 2), W - 8 - total)
        for i, c in enumerate(n["kids"]):
            c["_x"] = start + i * (w + GAP)
        # connectors: a trunk down from the parent, a bus, one drop into each child (orthogonal, drawn before boxes)
        py, ph = geo[n["level"]]
        cy, _ = geo[lv]
        bus = py + ph + (cy - py - ph) / 2
        xs = [c["_x"] + w / 2 for c in n["kids"]]
        lo, hi = min(xs + [pcx]), max(xs + [pcx])
        d = [f"M{pcx:.0f} {py + ph:.0f}V{bus:.0f}", f"M{lo:.0f} {bus:.0f}H{hi:.0f}"]
        d += [f"M{x:.0f} {bus:.0f}V{cy:.0f}" for x in xs]
        parts_lines.append(f'<path class="gt-line" d="{" ".join(d)}"/>')
    for n in walk(tree):
        w, size, sub = WIDE[n["level"]]
        y0, h = geo[n["level"]]
        parts_boxes.append(box(n, n["_x"], y0, w, h, n["_lines"], size, sub))
    return svg(slug + "-wide", "gt gt--wide", W, height, title, desc, parts_lines + parts_boxes)


NW = 360


def narrow(tree: dict, slug: str, title: str, desc: str) -> str:
    sizes = {0: (19, 13), 1: (16, 13), 2: (15, 13), 3: (14, 13)}
    indent = 22
    parts_lines, parts_boxes = [], []
    y = 4
    place = []
    for n in walk(tree):
        size, sub = sizes[n["level"]]
        x = 4 + n["level"] * indent
        w = NW - 4 - x
        h, lines = box_height(n, w, size, sub)
        h = max(h, 44)
        place.append((n, x, y, w, h, lines, size, sub))
        n["_ny"] = (x, y, h)
        y += h + 10
    for n in walk(tree):
        if not n["kids"]:
            continue
        x, y0, h = n["_ny"]
        sx = x + 11
        last = n["kids"][-1]["_ny"]
        d = [f"M{sx:.0f} {y0 + h:.0f}V{last[1] + last[2] / 2 - 8:.0f}"]
        for c in n["kids"]:
            cx, cy, ch = c["_ny"]
            mid = cy + ch / 2
            if c is n["kids"][-1]:
                d.append(f"M{sx:.0f} {mid - 8:.0f}Q{sx:.0f} {mid:.0f} {sx + 8:.0f} {mid:.0f}H{cx:.0f}")
            else:
                d.append(f"M{sx:.0f} {mid:.0f}H{cx:.0f}")
        parts_lines.append(f'<path class="gt-line" d="{" ".join(d)}"/>')
    for n, x, y0, w, h, lines, size, sub in place:
        parts_boxes.append(box(n, x, y0, w, h, lines, size, sub))
    return svg(slug + "-phone", "gt gt--phone", NW, y - 6, title, desc, parts_lines + parts_boxes)


def svg(slug: str, cls: str, w: float, h: float, title: str, desc: str, body: list[str]) -> str:
    return (f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" '
            f'aria-labelledby="{slug}-title {slug}-desc"><title id="{slug}-title">{esc(title)}</title>'
            f'<desc id="{slug}-desc">{esc(desc)}</desc>' + "".join(body) + "</svg>")


def describe(tree: dict) -> str:
    kids = [k for k in tree["kids"] if not k["more"]]
    bits = []
    for k in kids:
        if k["kids"]:
            steps = [s["label"] for s in k["kids"] if not s["more"]]
            bits.append(f'{k["label"]} ({STATE_WORD.get(k["state"], "")}), with its steps: ' + "; ".join(steps))
        else:
            bits.append(f'{k["label"]} ({STATE_WORD.get(k["state"], "")})')
    return f'{tree["label"]}, {tree["sub"]}. Under it: ' + ". ".join(bits) + "."


# ---- the fan-out: one voice note, many items, one inbox (E43-S9) -------------------------------------------------

def counts(text: str) -> dict:
    m = re.search(r"\*\*Counts: (.+?)\*\*", text)
    line = m.group(1)
    num = lambda pat: int(re.search(pat, line).group(1))  # noqa: E731
    c = {"ready": num(r"(\d+) ready"), "draft": num(r"(\d+) draft"), "asks": num(r"(\d+) asks"),
         "covered": num(r"(\d+) already covered"), "other": num(r"(\d+) for other teams")}
    c["total"] = len(re.findall(r"^\| \d+ \|", text, re.M))
    c["placed"] = sum(v for k, v in c.items() if k != "total")
    if c["placed"] < c["total"]:
        raise SystemExit(f"fan: the counts line ({line}) places fewer than the {c['total']} mapped items")
    return c


GROUPS = [("ready", "ready to build", "{n} built, each in its own thread"),
          ("asks", "questions for you", "{n} questions only you can answer"),
          ("draft", "drafts", "{n} ideas kept as drafts"),
          ("covered", "already planned", "{n} already in the plan"),
          ("other", "for other teams", "{n} passed to two other teams")]


def dots(x: float, y: float, n: int, per: int, cls: str) -> str:
    return "".join(f'<circle class="fan-dot {cls}" cx="{x + (i % per) * 14:.0f}" cy="{y + (i // per) * 14:.0f}" r="4.5"/>' for i in range(n))


def fan_box(x, y, w, h, name, sub, cls="") -> str:
    out = [f'<g class="fan-box {cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>',
           f'<text class="fan-name" x="{x + 16}" y="{y + 28}">{esc(name)}</text>']
    if sub:
        out.append(f'<text class="fan-sub" x="{x + 16}" y="{y + 50}">{esc(sub)}</text>')
    return "".join(out) + "</g>"


def wave(x, y) -> str:
    hs = [6, 14, 22, 12, 26, 18, 8, 20, 28, 14, 6, 16, 24, 10, 18, 6]
    return "".join(f'<rect class="fan-wave" x="{x + i * 7}" y="{y - h / 2:.0f}" width="3" height="{h}" rx="1.5"/>' for i, h in enumerate(hs))


def fan_wide(c: dict, minutes: int, day: str, slug: str, title: str, desc: str) -> str:
    H = 470
    lines, boxes = [], []
    # voice note
    boxes.append(fan_box(0, 176, 184, 118, "One voice note", f"{minutes} minutes, {day.rsplit(' ', 1)[0]}") + wave(16, 270))
    # the tree
    boxes.append(fan_box(232, 176, 184, 118, "Placed in the tree", f"{c['total']} items, each under", "fan-tree") +
                 '<text class="fan-sub" x="248" y="248">its goal in the tree</text>')
    lines.append('<path class="fan-line" d="M184 235H232"/>')
    # groups
    gy, gh, gap = 8, 78, 16
    gx, gw = 508, 300
    ys = []
    for i, (key, _, label) in enumerate(GROUPS):
        y = gy + i * (gh + gap)
        ys.append(y + gh / 2)
        n = c[key]
        cls = "fan-ask" if key == "asks" else ""
        boxes.append(f'<g class="fan-group {cls}"><rect x="{gx}" y="{y}" width="{gw}" height="{gh}" rx="2"/>'
                     f'<text class="fan-gname" x="{gx + 16}" y="{y + 26}">{esc(label.format(n=n))}</text>'
                     + dots(gx + 20, y + 48, n, 18, "fan-ask" if key == "asks" else "") + "</g>")
    # fan out: from the tree's right edge, one attach point per group, elbows at r=8
    for i, yc in enumerate(ys):
        ay = 176 + 118 * (i + 1) / (len(ys) + 1)
        # an upward line turns earlier the higher it goes, a downward one the lower it goes, so no two cross
        mx = 452 + (i if yc <= ay else len(ys) - 1 - i) * 10
        lines.append(elbow(416, ay, mx, yc, gx))
    # fan in to the inbox
    ix, iy, iw, ih = 900, 176, 164, 118
    for i, yc in enumerate(ys):
        ay = iy + ih * (i + 1) / (len(ys) + 1)
        mx = 836 + (len(ys) - 1 - i) * 10 if yc < ay else 836 + i * 10
        lines.append(elbow(gx + gw, yc, mx, ay, ix))
    boxes.append(fan_box(ix, iy, iw, ih, "One inbox", "only what needs you", "fan-inbox"))
    # the two kinds of card
    kx, kw = 1100, 100
    for i, (name, sub, cls) in enumerate([("Blocked", "on you", "fan-ask"), ("Done", "for approval", "")]):
        ky = 120 + i * 150
        lines.append(elbow(ix + iw, iy + ih * (i + 1) / 3, 1082, ky + 40, kx))
        boxes.append(fan_box(kx, ky, kw, 80, name, sub, "fan-kind " + cls))
    return svg(slug + "-wide", "fan fan--wide", 1200, H, title, desc, lines + boxes)


def elbow(x1, y1, mx, y2, x2, r=8) -> str:
    """A right-angle connector: across to mx, down or up to y2, across to x2, corners rounded at r."""
    if abs(y2 - y1) < 1:
        return f'<path class="fan-line" d="M{x1:.0f} {y1:.0f}H{x2:.0f}"/>'
    s = 1 if y2 > y1 else -1
    r = min(r, abs(y2 - y1) / 2)
    return (f'<path class="fan-line" d="M{x1:.0f} {y1:.1f}H{mx - r:.0f}Q{mx:.0f} {y1:.1f} {mx:.0f} {y1 + s * r:.1f}'
            f'V{y2 - s * r:.1f}Q{mx:.0f} {y2:.1f} {mx + r:.0f} {y2:.1f}H{x2:.0f}"/>')


def fan_phone(c: dict, minutes: int, day: str, slug: str, title: str, desc: str) -> str:
    lines, boxes = [], []
    w = NW
    boxes.append(fan_box(40, 0, 280, 96, "One voice note", f"{minutes} minutes, {day.rsplit(' ', 1)[0]}") + wave(56, 74))
    lines.append('<path class="fan-line" d="M180 96V124"/>')
    boxes.append(fan_box(40, 124, 280, 72, "Placed in the tree", f"{c['total']} items, each under its goal", "fan-tree"))
    y = 236
    rows = []
    for key, _, label in GROUPS:
        n = c[key]
        h = 44 + ((n - 1) // 18 + 1) * 14
        cls = "fan-ask" if key == "asks" else ""
        boxes.append(f'<g class="fan-group {cls}"><rect x="40" y="{y}" width="280" height="{h}" rx="2"/>'
                     f'<text class="fan-gname" x="56" y="{y + 24}">{esc(label.format(n=n))}</text>'
                     + dots(60, y + 40, n, 18, cls) + "</g>")
        rows.append(y + 24)
        y += h + 12
    # out on the left rail, back in on the right rail
    lines.append(f'<path class="fan-line" d="M140 196V214Q140 222 132 222H28Q20 222 20 230V{rows[-1] - 8}"/>')
    for ry in rows:
        lines.append(f'<path class="fan-line" d="M20 {ry - 8}Q20 {ry} 28 {ry}H40"/>')
        lines.append(f'<path class="fan-line" d="M320 {ry}H332Q340 {ry} 340 {ry + 8}V{y + 4}"/>')
    lines.append(f'<path class="fan-line" d="M340 {y + 4}Q340 {y + 12} 332 {y + 12}H180V{y + 28}"/>')
    iy = y + 28
    boxes.append(fan_box(40, iy, 280, 72, "One inbox", "only what needs you", "fan-inbox"))
    ky = iy + 108
    lines.append(f'<path class="fan-line" d="M110 {iy + 72}V{ky}"/><path class="fan-line" d="M250 {iy + 72}V{ky}"/>')
    boxes.append(fan_box(40, ky, 132, 64, "Blocked", "on you", "fan-kind fan-ask"))
    boxes.append(fan_box(188, ky, 132, 64, "Done", "for approval", "fan-kind"))
    return svg(slug + "-phone", "fan fan--phone", w, ky + 68, title, desc, lines + boxes)


# ---- write into the pages -----------------------------------------------------------------------------------------

def put(text: str, name: str, block: str) -> str:
    begin, end = f"<!-- goal-tree:{name} begin (tools/goal_tree.py writes this) -->", f"<!-- goal-tree:{name} end -->"
    i, j = text.find(begin), text.find(end)
    if i < 0 or j < 0:
        raise SystemExit(f"{name}: the page has no goal-tree:{name} markers")
    return text[:i + len(begin)] + "\n" + block + "\n" + text[j:]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", action="append", default=[], help="name=path, one per repo the config names")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    cfg = json.loads((SITE / "tools" / "goal-trees.json").read_text(encoding="utf-8"))
    paths = dict(r.split("=", 1) for r in a.repo)
    repos = {k: Repo(Path(v).expanduser().resolve()) for k, v in paths.items()}
    blocks: dict[str, dict[str, str]] = {}
    for name, spec in cfg["trees"].items():
        tree = build(spec, repos[spec["repo"]])
        desc = describe(tree)
        block = wide(tree, f"gt-{name}", spec["title"], desc) + "\n" + narrow(build(spec, repos[spec["repo"]]), f"gt-{name}", spec["title"], desc)
        blocks.setdefault(spec["page"], {})[name] = block
    f = cfg["fan"]
    c = counts((repos[f["repo"]].root / f["source"]).read_text(encoding="utf-8"))
    title = "One voice note fans out into many threads and back into one inbox"
    desc = (f"One {f['minutes']}-minute voice note of {f['day']} became {c['total']} items placed in the goal tree, {c['placed'] - c['total']} of them in two places: "
            + ", ".join(g[2].format(n=c[g[0]]) for g in GROUPS)
            + ". Everything that needs its owner comes back to one inbox, as two kinds of card: blocked on you, or done and waiting for your approval.")
    blocks.setdefault(f["page"], {})["fan"] = fan_wide(c, f["minutes"], f["day"], "fan", title, desc) + "\n" + fan_phone(c, f["minutes"], f["day"], "fan", title, desc)
    bad = []
    for page, named in blocks.items():
        for name, block in named.items():
            for word in cfg["private"]:
                if word in re.sub(r"<[^>]+>", " ", block).lower():
                    bad.append(f"{page} {name}: carries the private word {word!r}")
    if bad:
        print("\n".join(bad), file=sys.stderr)
        return 1
    stale = []
    for page, named in blocks.items():
        p = SITE / page
        old = p.read_text(encoding="utf-8")
        new = old
        for name, block in named.items():
            new = put(new, name, block)
        if new != old:
            stale.append(page)
            if not a.check:
                p.write_text(new, encoding="utf-8")
    print(("differs: " if a.check else "wrote: ") + (", ".join(stale) or "nothing (pages already match the repos)"))
    return 1 if (a.check and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
