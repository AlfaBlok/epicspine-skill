"""Operating learnings stay strict-valid, one-line, and depth-scoped."""
from __future__ import annotations

import re
from pathlib import Path
import tempfile
import unittest

from test_validate_spine import validate_spine as v

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "examples"
TEMPLATES = ROOT / "skill/epic-spine/assets"

LEARNING_LINE = re.compile(r"^L-\d+ \| .+ \| .+ \| .+ \| confirmed \d{4}-\d{2}-\d{2}$")


def learning_lines(section: str) -> list[str]:
    return [
        line.strip()[2:].strip()
        for line in section.splitlines()
        if line.strip().startswith("- L-")
    ]


class OperatingLearningsTests(unittest.TestCase):
    def document(self, text: str):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EPIC.md"
            path.write_text(text, encoding="utf-8")
            return v.validate_local(path)

    def test_root_example_has_strict_always_and_scoped_index(self) -> None:
        document = v.validate_local(EXAMPLES / "EPIC-0-CLI-EXAMPLE.md")
        self.assertEqual([], document.errors)
        self.assertEqual([], document.warnings)
        section = document.sections["Operating Learnings"]
        self.assertLess(section.index("**Always**"), section.index("**Scoped index**"))
        lines = learning_lines(section)
        self.assertGreaterEqual(len(lines), 2)
        self.assertTrue(all(LEARNING_LINE.match(line) for line in lines), lines)

    def test_child_example_holds_exactly_one_scoped_learning(self) -> None:
        document = v.validate_local(EXAMPLES / "rollups/child.md")
        self.assertEqual([], document.errors)
        self.assertEqual([], document.warnings)
        lines = learning_lines(document.sections["Operating Learnings"])
        self.assertEqual(1, len(lines))
        self.assertTrue(LEARNING_LINE.match(lines[0]), lines)

    def test_synthetic_root_with_always_and_scoped_index_passes_strict(self) -> None:
        source = (EXAMPLES / "rollups/root.md").read_text()
        section = (
            "## Operating Learnings\n\n"
            "**Always** (every task; read in full at bind):\n\n"
            "- L-1 | any change | run the suite before handoff | broken main blocks everyone | confirmed 2026-10-01\n\n"
            "**Scoped index** (follow only when the trigger matches):\n\n"
            "| Applies when | Learning lives in |\n|---|---|\n"
            "| touching the validator | [child](child.md) |\n\n"
        )
        document = self.document(source.replace("## Current State", section + "## Current State", 1))
        self.assertEqual([], document.errors)
        self.assertEqual([], document.warnings)
        self.assertFalse(document.fails(strict=True))
        self.assertGreaterEqual(len(learning_lines(document.sections["Operating Learnings"])), 1)

    def test_templates_carry_the_section_without_learning_diagnostics(self) -> None:
        for name in ("epic-spine-template.md", "compact-spine-template.md"):
            with self.subTest(template=name):
                document = v.validate_local(TEMPLATES / name)
                self.assertIn("Operating Learnings", document.sections)
                self.assertFalse(any("learn" in message.lower() for message in document.errors))
                self.assertFalse(any("learn" in message.lower() for message in document.warnings))


if __name__ == "__main__":
    unittest.main()
