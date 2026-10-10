"""Book drift guard: index.html must reflect the skill and stay self-contained.

The Book deck (``index.html``) is the human surface of this repository, which is
at once the skill source, its own root spine and its own Book. When the skill
gains a reference, script or asset, the deck must name it or the three surfaces
have diverged. This test fails loudly so the next agent knows to update the deck.

Policy:
- every file under ``skill/epic-spine/references|scripts|assets`` must be named
  by its basename somewhere in the deck, unless it is listed in ``ALLOWLIST``
  with a reason;
- the deck must not load anything from an external URL (the HTML must stay
  self-contained); the only permitted external links are to the canonical
  repository in the "Where to go next" slide;
- every ``#N`` deep link must point at a real slide;
- every path-like token inside ``<code>`` must resolve to a real file.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BOOK = ROOT / "index.html"
SKILL_DIR = ROOT / "skill" / "epic-spine"

# Files intentionally not named in the deck. Each entry needs a reason.
ALLOWLIST: dict[str, str] = {}

SKILL_FOLDERS = ("references", "scripts", "assets")

ALLOWED_EXTERNAL = "github.com/AlfaBlok/epicspine-skill"
URL_RE = re.compile(r"""(?:src|href)\s*=\s*["']\s*(https?://[^"'\s>]+)""", re.I)
CSS_URL_RE = re.compile(r"""url\(\s*["']?\s*(https?://[^)"'\s>]+)""", re.I)
HASH_RE = re.compile(r"""href\s*=\s*["']#(\d+)["']""", re.I)
SLIDE_RE = re.compile(r"""<section\s+class=["']slide""", re.I)
CODE_RE = re.compile(r"<code>(.*?)</code>", re.S)
# A token is path-like only when it has a directory separator and a known suffix.
PATH_RE = re.compile(
    r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.~-]+)+\.(?:md|markdown|py|json|html|sha256|sh|txt|ya?ml|toml)\b"
)


def book_text() -> str:
    return BOOK.read_text(encoding="utf-8")


def skill_files() -> list[Path]:
    files: list[Path] = []
    for folder in SKILL_FOLDERS:
        files.extend(sorted(p for p in (SKILL_DIR / folder).glob("*") if p.is_file()))
    return files


class BookDriftTests(unittest.TestCase):
    def test_every_skill_file_is_named_in_the_deck(self) -> None:
        text = book_text()
        missing = [
            path.name
            for path in skill_files()
            if path.name not in ALLOWLIST and path.name not in text
        ]
        self.assertEqual(
            [],
            missing,
            "skill files absent from the Book deck: "
            f"{missing}. Fix: add the file to the Book deck (index.html) or "
            "allowlist it with a reason in tests/test_book_drift.py.",
        )

    def test_deck_loads_nothing_external(self) -> None:
        text = book_text()
        urls = URL_RE.findall(text) + CSS_URL_RE.findall(text)
        external = [url for url in urls if ALLOWED_EXTERNAL not in url]
        self.assertEqual(
            [],
            external,
            "the deck must not load external resources "
            f"(found {external}); keep it self-contained or link only to "
            f"{ALLOWED_EXTERNAL}.",
        )

    def test_every_hash_link_targets_a_slide(self) -> None:
        text = book_text()
        slides = len(SLIDE_RE.findall(text))
        self.assertGreater(slides, 0, "no slides found in index.html")
        targets = [int(n) for n in HASH_RE.findall(text)]
        bad = sorted({n for n in targets if n < 1 or n > slides})
        self.assertEqual(
            [],
            bad,
            f"deep links point outside the {slides} slides: {bad}. "
            "Fix: repoint the #N link at a real slide.",
        )

    def test_code_paths_exist(self) -> None:
        text = book_text()
        checked = 0
        missing: list[str] = []
        for block in CODE_RE.findall(text):
            for token in PATH_RE.findall(block):
                checked += 1
                if not (ROOT / token).exists():
                    missing.append(token)
        self.assertEqual(
            [],
            sorted(set(missing)),
            "path-like tokens in <code> do not exist on disk: "
            f"{sorted(set(missing))}. Fix: correct the path or remove it from "
            "the Book deck (index.html).",
        )
        self.assertGreater(checked, 0, "no path-like <code> tokens were checked")

    def test_counter_total_matches_slide_count(self) -> None:
        text = book_text()
        slides = len(SLIDE_RE.findall(text))
        match = re.search(r'id="counter">\s*1 / (\d+)<', text)
        self.assertIsNotNone(match, "slide counter markup not found")
        self.assertEqual(
            slides,
            int(match.group(1)),
            "the initial slide counter total must equal the number of slides. "
            "Fix: update the counter in index.html.",
        )

    def test_every_diagram_is_an_accessible_figure(self) -> None:
        text = book_text()
        svgs = re.findall(r"<svg\b[^>]*>.*?</svg>", text, re.S)
        self.assertGreater(len(svgs), 10, "expected the deck to carry inline diagrams")
        ids: list[str] = []
        for svg in svgs:
            head = svg[: svg.index(">") + 1]
            self.assertIn('role="img"', head, f"diagram without role=img: {head[:80]}")
            labelled = re.search(r'aria-labelledby="([^"]+)"', head)
            self.assertIsNotNone(labelled, f"diagram without aria-labelledby: {head[:80]}")
            title_id, desc_id = labelled.group(1).split()
            body = svg[len(head):]
            self.assertTrue(
                body.startswith(f'<title id="{title_id}">'),
                f"<title> must be the first child of {title_id}",
            )
            self.assertIn(f'<desc id="{desc_id}">', body)
            ids += [title_id, desc_id]
        self.assertEqual(len(ids), len(set(ids)), "diagram title/desc ids must be unique")

    def test_diagrams_carry_no_shadows(self) -> None:
        text = book_text()
        css = "\n".join(re.findall(r"<style>(.*?)</style>", text, re.S))
        self.assertNotRegex(css, r"box-shadow|drop-shadow|text-shadow")


if __name__ == "__main__":
    unittest.main()
