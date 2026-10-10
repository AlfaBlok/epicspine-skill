"""Line budgets and no-orphan checks for the EpicSpine skill.

Ratchet policy: budgets may be LOWERED freely; a budget may be RAISED only with a
recorded reason (a comment here or in the commit message). Pre-existing files are
pinned to their line count rounded up to the next multiple of 5; grandfathered
files that already exceed the new-file cap are pinned at their exact current size
and may only shrink. Rounded budgets leave slack: a file below its rounded budget
is expected, so a passing check does not mean the file sits exactly at the limit.
New references, assets, and scripts are capped at 200 lines and `SKILL.md` at 150,
so a cold agent never loads a runaway kernel.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL_DIR = ROOT / "skill" / "epic-spine"
SKILL = SKILL_DIR / "SKILL.md"
EXAMPLES = ROOT / "examples"

SKILL_MAX = 150
NEW_FILE_MAX = 200
ALWAYS_MAX = 12

# Pre-existing files: budget = current line count rounded up to the next 5.
# operating-model.md, epic-spine-template.md, and validate_spine.py are
# grandfathered (already over the 200-line new-file cap) and pinned exactly: they
# may only shrink. The other scripts are pre-existing and pinned to rounded sizes.
EXISTING_BUDGETS = {
    "references/book-companion.md": 155,
    "references/compact-state.md": 60,
    "references/execution-rollups.md": 70,
    "references/git-doctrine.md": 65,
    "references/hygiene.md": 50,
    "references/learnings.md": 70,
    "references/operating-model.md": 497,
    "references/roles-and-dispatch.md": 105,  # raised: ask-once-and-record rule (dispatch defaults)
    "references/skill-update.md": 55,  # +5: central-install note, 2026-10-09
    "references/structural-validation.md": 60,
    "references/ticket-backends.md": 80,
    "assets/book-companion-contract.md": 25,
    "assets/compact-spine-template.md": 65,
    "assets/dispatch-prompt-preamble.md": 35,
    "assets/epic-spine-template.md": 292,
    "assets/github-issue-template.md": 85,
    "assets/sweep-brief.md": 25,
    "scripts/migrate_spine.py": 170,
    "scripts/rollup_spine.py": 398,
    "scripts/skill_update.py": 485,  # raised: tree-based freshness + symlink resolution, 2026-10-10
    "scripts/validate_spine.py": 1032,
}

# Files authored by the lean-kernel change: hard-capped instead of pinned.
NEW_FILES = {
    "references/artifacts.md",
    "references/dispatch-prompts.md",
    "references/role-protocols.md",
    "references/spine-creation.md",
    "references/spine-model.md",
    "references/sprint-dialect-v2.md",
}

LEARNING_LINE = re.compile(r"^- L-\d+ ")


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def skill_files() -> list[Path]:
    files: list[Path] = []
    for folder in ("references", "assets", "scripts"):
        files.extend(
            sorted(p for p in (SKILL_DIR / folder).glob("*") if p.is_file())
        )
    return files


class BudgetTests(unittest.TestCase):
    def test_skill_md_within_kernel_budget(self) -> None:
        self.assertLessEqual(line_count(SKILL), SKILL_MAX)

    def test_new_references_within_cap(self) -> None:
        # Any reference/asset/script not pinned in EXISTING_BUDGETS is "new": capped.
        for folder in ("references", "assets", "scripts"):
            for path in sorted((SKILL_DIR / folder).glob("*")):
                if not path.is_file():
                    continue
                rel = str(path.relative_to(SKILL_DIR))
                if rel in EXISTING_BUDGETS:
                    continue
                with self.subTest(file=rel):
                    self.assertLessEqual(line_count(path), NEW_FILE_MAX)
        for rel in sorted(NEW_FILES):
            with self.subTest(file=rel):
                self.assertTrue((SKILL_DIR / rel).is_file(), f"missing new file {rel}")

    def test_existing_files_do_not_grow_past_budget(self) -> None:
        for rel, budget in sorted(EXISTING_BUDGETS.items()):
            with self.subTest(file=rel):
                path = SKILL_DIR / rel
                self.assertTrue(path.is_file(), f"missing existing file {rel}")
                self.assertLessEqual(
                    line_count(path), budget, f"{rel} grew past its budget {budget}"
                )

    def test_example_always_blocks_within_cap(self) -> None:
        checked = 0
        for path in sorted(EXAMPLES.rglob("*.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                if line.strip() != "## Operating Learnings":
                    continue
                cursor = index + 1
                while (
                    cursor < len(lines)
                    and not lines[cursor].startswith("## ")
                    and "**Always**" not in lines[cursor]
                ):
                    cursor += 1
                if cursor >= len(lines) or "**Always**" not in lines[cursor]:
                    break  # branch-scope learnings, no Always block
                cursor += 1
                block: list[str] = []
                while (
                    cursor < len(lines)
                    and not lines[cursor].startswith("## ")
                    and not lines[cursor].strip().startswith("**")
                ):
                    if LEARNING_LINE.match(lines[cursor].strip()):
                        block.append(lines[cursor])
                    cursor += 1
                checked += 1
                self.assertLessEqual(
                    len(block), ALWAYS_MAX, f"{path} Always block exceeds {ALWAYS_MAX}"
                )
        self.assertGreaterEqual(checked, 1, "no root Operating Learnings Always block found")

    def test_skill_md_links_every_skill_file(self) -> None:
        # No orphans: each skill file must be an exact backticked token in a table
        # row, not merely a substring anywhere in the kernel.
        rows = "\n".join(
            line
            for line in SKILL.read_text(encoding="utf-8").splitlines()
            if line.lstrip().startswith("|")
        )
        missing = [
            str(path.relative_to(SKILL_DIR))
            for path in skill_files()
            if f"`{path.relative_to(SKILL_DIR)}`" not in rows
        ]
        self.assertEqual([], missing, f"SKILL.md does not link: {missing}")


if __name__ == "__main__":
    unittest.main()
