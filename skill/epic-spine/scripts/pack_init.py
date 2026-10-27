"""`pack.py init NAME --repo PATH`: write a pack's missing files and sections (references/packs.md "Init").

Never overwrites. A missing file is written from its sections' headings and columns (heading null = the file's one
table; computed columns are left out: the export derives them); a file that exists only gains the sections it lacks,
appended at its end; a missing spine (`docs/spines/`) is never created, only noted; a `dir` gets a `.gitkeep`; per-item
files (`many`) are not pre-made. AGENTS.md gains `Pack: NAME` if absent. Idempotent: a second run changes nothing."""
from __future__ import annotations

import argparse
from pathlib import Path

import pack
import pack_md as md


def section_text(s: dict) -> str:
    cols = [f["column"] for f in s.get("fields", {}).values() if "computed" not in f]
    rows = f"| {' | '.join(cols)} |\n|{'---|' * len(cols)}\n" if s["shape"] == "table" else ""
    return (f"## {s['heading']}\n\n" if s["heading"] else "") + rows


def missing(text: str | None, s: dict) -> bool:
    return md.body(text, s["heading"]) is None if s["heading"] else md.table(text) is None


def init(repo: Path, name: str, notes: list[str] | None = None) -> list[str]:
    """What it changed, one line each ([] when the repo already has everything); what it skipped goes to `notes`."""
    schema, done, layout, notes = pack.load(name), [], {}, [] if notes is None else notes
    for f in schema["files"].values():
        if f.get("dir") and not (repo / f["dir"]).is_dir():
            (repo / f["dir"]).mkdir(parents=True)
            (repo / f["dir"] / ".gitkeep").write_text("", encoding="utf-8")
            done.append(f"created {f['dir']}")
        for s in [] if f.get("many") else f["sections"].values():
            layout.setdefault(md.where(f, s), (f, []))[1].append(s)
    for rel, (f, secs) in layout.items():
        path = repo / rel
        text = path.read_text(encoding="utf-8") if path.is_file() else None
        if text is None and rel.startswith("docs/spines/"):
            notes.append(f"skipped {rel}: no such spine (create it, then rerun init for its " + ", ".join(f"## {s['heading']}" for s in secs) + ")")
            continue
        add = [s for s in secs if missing(text, s)]
        if not add:
            continue
        chunks = "\n".join(section_text(s) for s in add)
        if text is None:
            title = path.stem.replace("-", " ").replace("_", " ").capitalize()
            intro = f"{f['doc']}\n\n" if rel == f["path"] and f.get("doc") else ""
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {title}\n\n{intro}{chunks}", encoding="utf-8")
        else:
            path.write_text(text.rstrip("\n") + "\n\n" + chunks, encoding="utf-8")
        what = ", ".join(f"## {s['heading']}" if s["heading"] else "its table" for s in add)
        done.append(f"{'created' if text is None else 'added to'} {rel}: {what}")
    if name not in pack.enabled(repo):
        agents = repo / "AGENTS.md"
        old = agents.read_text(encoding="utf-8").rstrip("\n") + "\n\n" if agents.is_file() else "# AGENTS.md\n\n"
        agents.write_text(f"{old}Pack: {name}\n", encoding="utf-8")
        done.append(f"AGENTS.md: added Pack: {name}")
    return done


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pack.py init", description=__doc__.splitlines()[0])
    ap.add_argument("name", choices=pack.available())
    ap.add_argument("--repo", type=Path, required=True)
    a = ap.parse_args(argv)
    notes: list[str] = []
    done = init(a.repo.resolve(), a.name, notes)
    print("\n".join(done + notes + ([] if done else [f"{a.name}: nothing to do (already initialised)"])))
    return 0
