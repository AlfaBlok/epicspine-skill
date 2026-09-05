from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR_PATH = (
    Path(__file__).parents[1]
    / "skill"
    / "epic-spine"
    / "scripts"
    / "validate_spine.py"
)
SPEC = importlib.util.spec_from_file_location("validate_spine", VALIDATOR_PATH)
assert SPEC and SPEC.loader
validate_spine = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_spine
SPEC.loader.exec_module(validate_spine)


def spine_text(
    *,
    spine_id: str,
    spine_type: str,
    root: str,
    parent: str,
    spine_map: str = "No child spines.",
    rationale: str = "n/a",
    decisions: str | None = None,
) -> str:
    decision_rows = decisions or (
        "| 2026-08-16 | accepted | Use the connected hierarchy | "
        "It gives every branch one owner. | issue-1 | n/a |"
    )
    return f"""# EPIC: Test

Status: active
Created: 2026-08-16
Updated: 2026-08-16
Repository: example/repo
Primary document: docs/{spine_id}.md
Spine ID: {spine_id}
Spine Type: {spine_type}
Root spine: {root}
Parent spine: {parent}
Additional root rationale: {rationale}
GitHub issues: example/repo/issues
Integration branch: main
Active spine steward: codex-test
Steward since: 2026-08-16 12:00 UTC
Last reconciled commit: abc1234
Planner: codex-test
Worker: codex-test
Tester: codex-test

## Role Bindings

Configured for the test steward.

## Write Scope

Bound spine: this document

## Authority By Artifact

This spine owns intent and rollup state.

## Spine Map

{spine_map}

## Mission

Prove the connected-spine contract.

## Definition Of Done

- [ ] Graph validation passes.

## Current State

Phase: implementation
Next action: Run validation.

## Execution Cursor

Last attempted: Created the fixture.
Result: Fixture is ready.
Execution status: active
Waiting on: nothing
Approved work: Run all validation tests.
Next action: Run validation.

## Bootstrap Map

Read this document.

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
{decision_rows}

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Acceptance | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| draft | Planner | codex-test | Validate graph | draft | - | - | abc1234 | Tests pass | - | 2026-08-16 12:00 UTC | Run tests |

## Branch And Integration

Integration target is main.

## Human Gates

None.

## Recovery And Takeover

Resume from the cursor.

## Validation Evidence

Pending.

## Handoff Journal

Pending.

## Open Questions

None.
"""


class ValidateSpineTests(unittest.TestCase):
    def write(self, folder: Path, name: str, content: str) -> Path:
        path = folder / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_valid_root_and_child_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            child_row = (
                "| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | "
                "Latest Evidence | Last Rolled Up | Next Action |\n"
                "|---|---|---|---|---|---|---|---|---|\n"
                "| alpha | child | [Alpha](alpha.md) | Deliver alpha | active | healthy | "
                "issue-1 | 2026-08-16 12:00 UTC | Continue delivery |"
            )
            root = self.write(
                folder,
                "root.md",
                spine_text(spine_id="root", spine_type="root", root="self", parent="none", spine_map=child_row),
            )
            child = self.write(
                folder,
                "alpha.md",
                spine_text(
                    spine_id="alpha",
                    spine_type="branch",
                    root="[root](root.md)",
                    parent="[root](root.md)",
                ),
            )
            documents = [validate_spine.validate_local(root), validate_spine.validate_local(child)]
            validate_spine.validate_graph(documents)
            self.assertEqual([], [error for doc in documents for error in doc.errors])

    def test_parent_must_register_child(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root = self.write(folder, "root.md", spine_text(spine_id="root", spine_type="root", root="self", parent="none"))
            child = self.write(
                folder,
                "alpha.md",
                spine_text(
                    spine_id="alpha",
                    spine_type="branch",
                    root="[root](root.md)",
                    parent="[root](root.md)",
                ),
            )
            documents = [validate_spine.validate_local(root), validate_spine.validate_local(child)]
            validate_spine.validate_graph(documents)
            self.assertTrue(any("does not reciprocally register" in error for error in documents[1].errors))

    def test_parent_cycle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root = self.write(folder, "root.md", spine_text(spine_id="root", spine_type="root", root="self", parent="none"))
            a_row = (
                "| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |\n"
                "|---|---|---|---|---|---|---|---|---|\n"
                "| b | child | [B](b.md) | B | active | healthy | issue-1 | 2026-08-16 12:00 UTC | Continue |"
            )
            b_row = (
                "| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |\n"
                "|---|---|---|---|---|---|---|---|---|\n"
                "| a | child | [A](a.md) | A | active | healthy | issue-2 | 2026-08-16 12:00 UTC | Continue |"
            )
            a = self.write(
                folder,
                "a.md",
                spine_text(spine_id="a", spine_type="branch", root="[root](root.md)", parent="[B](b.md)", spine_map=a_row),
            )
            b = self.write(
                folder,
                "b.md",
                spine_text(spine_id="b", spine_type="branch", root="[root](root.md)", parent="[A](a.md)", spine_map=b_row),
            )
            documents = [validate_spine.validate_local(path) for path in (root, a, b)]
            validate_spine.validate_graph(documents)
            self.assertTrue(any("parent cycle detected" in error for doc in documents for error in doc.errors))

    def test_multiple_unexplained_roots_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            first = self.write(folder, "one.md", spine_text(spine_id="one", spine_type="root", root="self", parent="none"))
            second = self.write(folder, "two.md", spine_text(spine_id="two", spine_type="root", root="self", parent="none"))
            documents = [validate_spine.validate_local(first), validate_spine.validate_local(second)]
            validate_spine.validate_graph(documents)
            self.assertTrue(any("exactly one canonical root" in error for doc in documents for error in doc.errors))

    def test_additional_root_with_rationale_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            canonical = self.write(
                folder,
                "canonical.md",
                spine_text(spine_id="canonical", spine_type="root", root="self", parent="none"),
            )
            independent = self.write(
                folder,
                "independent.md",
                spine_text(
                    spine_id="independent",
                    spine_type="root",
                    root="self",
                    parent="none",
                    rationale="Separate repository and integration authority.",
                ),
            )
            documents = [validate_spine.validate_local(canonical), validate_spine.validate_local(independent)]
            validate_spine.validate_graph(documents)
            self.assertEqual([], [error for doc in documents for error in doc.errors])

    def test_rejected_decision_requires_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(
                Path(tmp),
                "root.md",
                spine_text(
                    spine_id="root",
                    spine_type="root",
                    root="self",
                    parent="none",
                    decisions="| 2026-08-16 | rejected | Try a second root | It fragments state. | - | never |",
                ),
            )
            document = validate_spine.validate_local(path)
            self.assertTrue(any("rejected but Evidence is empty" in error for error in document.errors))


class MarkdownParserTests(unittest.TestCase):
    def source(self) -> str:
        return spine_text(spine_id="root", spine_type="root", root="self", parent="none")

    def validate_source(self, source: str):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "root.md"
            path.write_text(source, encoding="utf-8")
            return validate_spine.validate_local(path)

    def test_malformed_active_and_done_rows_fail_with_source_line(self):
        for status in ("active", "done"):
            for malformed in ("extra", "missing"):
                source = self.source()
                original = next(line for line in source.splitlines() if line.startswith("| draft | Planner"))
                row = original.replace("| draft | Planner", "| #10 | Planner").replace("| draft | - |", f"| {status} | - |")
                row = row + " extra |" if malformed == "extra" else row.rsplit("|", 2)[0] + "|"
                source = source.replace(original, row)
                line = source.splitlines().index(row) + 1
                result = self.validate_source(source)
                self.assertTrue(any(f"Issue Ledger line {line}: malformed table row" in error for error in result.errors), result.errors)

    def test_short_row_and_empty_edge_cells_are_not_dropped(self):
        errors = []
        header, rows = validate_spine.parse_table("| A | B | C |\n|---|---|---|\n|| x ||\n| short |", errors=errors)
        self.assertEqual(["A", "B", "C"], header)
        self.assertEqual([["", "x", ""]], rows)
        self.assertTrue(any("line 4" in error and "expected 3 cells, found 1" in error for error in errors))

    def test_escaped_pipes_preserve_rows_and_semantic_checks(self):
        source = self.source().replace("Validate graph", r"Validate graph \| parser")
        self.assertEqual([], self.validate_source(source).errors)
        source = source.replace("| draft | - |", "| done | - |")
        self.assertTrue(any("done without evidence" in error for error in self.validate_source(source).errors))
        header, rows = validate_spine.parse_table("| A | B |\n|:---|---:|\n| `left \\| right` | final \\|\n")
        self.assertEqual(["A", "B"], header)
        self.assertEqual([["left | right", "final |"]], rows)

    def test_even_backslashes_do_not_escape_a_delimiter(self):
        errors = []
        _, rows = validate_spine.parse_table("| A | B |\n|---|---|\n| slash " + "\\" * 2 + "| value |", errors=errors)
        self.assertEqual([["slash " + "\\" * 2, "value"]], rows)
        self.assertEqual([], errors)

    def test_invalid_or_missing_separator_fails(self):
        for separator in ("| invalid |---|", "|---|", "|--|---|"):
            with self.subTest(separator=separator):
                errors = []
                validate_spine.parse_table(f"| A | B |\n{separator}\n| x | y |", errors=errors)
                self.assertTrue(any("line 2: invalid table separator" in error for error in errors))
        errors = []
        validate_spine.parse_table("| A | B |", errors=errors)
        self.assertTrue(any("missing its separator row" in error for error in errors))
        source = self.source().replace("|---|---|---|---|---|---|", "|bad|---|---|---|---|---|", 1)
        self.assertTrue(any("Decisions line" in error and "invalid table separator" in error for error in self.validate_source(source).errors))

    def test_separate_tables_are_not_combined(self):
        errors = []
        section = "| A | B |\n|---|---|\n| first | row |\n\nExplanation.\n\n| C | D |\n|---|---|\n| second | row |"
        header, rows = validate_spine.parse_table(section, errors=errors)
        self.assertEqual(["A", "B"], header)
        self.assertEqual([["first", "row"]], rows)
        self.assertTrue(any("line 7: additional table block" in error for error in errors))
        source = self.source().replace("## Branch And Integration", "| Other | Table |\n|---|---|\n| done | - |\n\n## Branch And Integration")
        self.assertTrue(any("Issue Ledger line" in error and "additional table block" in error for error in self.validate_source(source).errors))

    def test_empty_fields_do_not_consume_the_following_line(self):
        for newline in ("\n", "\r\n"):
            text = newline.join(["Last attempted:  ", "Result: Retained result.", "Next action:", ""])
            self.assertEqual({"Last attempted": "", "Result": "Retained result.", "Next action": ""}, validate_spine.parse_key_values(text))
        source = self.source().replace("Last attempted: Created the fixture.", "Last attempted:")
        result = self.validate_source(source)
        self.assertIn("Execution Cursor unresolved field: Last attempted", result.warnings)
        self.assertNotIn("Execution Cursor missing field: Result", result.errors)
        self.assertEqual("Fixture is ready.", validate_spine.parse_key_values(result.sections["Execution Cursor"])["Result"])


ROOT = Path(__file__).parents[1]
SCRIPT = VALIDATOR_PATH
validator = validate_spine


class ValidatorCompatibilityTests(unittest.TestCase):
    def test_v1_template_has_only_warnings_for_v2_rules(self):
        result = validator.validate(ROOT / "skill/epic-spine/assets/epic-spine-template.md")
        self.assertEqual([], result["errors"])
        self.assertTrue(result["warnings"])

    def test_default_cli_keeps_v1_compatible_but_strict_promotes_warnings(self):
        template = ROOT / "skill/epic-spine/assets/epic-spine-template.md"
        default = subprocess.run([sys.executable, str(SCRIPT), str(template)], check=False)
        strict = subprocess.run([sys.executable, str(SCRIPT), "--strict", str(template)], check=False)
        self.assertEqual(0, default.returncode)
        self.assertEqual(1, strict.returncode)

    def test_superseded_redirect_warning(self):
        source = (ROOT / "skill/epic-spine/assets/epic-spine-template.md").read_text()
        source = source.replace("Status: draft | ready | active | pending — DISPATCH ONLY AFTER <condition> | CLOSED | ON HOLD | SUPERSEDED by <path> — do not execute from this document", "Status: SUPERSEDED")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(source)
            path = Path(handle.name)
        try:
            result = validator.validate(path)
            self.assertTrue(any("SUPERSEDED status" in warning for warning in result["warnings"]))
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
