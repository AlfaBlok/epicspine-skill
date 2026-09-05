from __future__ import annotations

import importlib.util
import json
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
                row = original.replace("| draft | Planner", "| https://github.com/example/repo/issues/10 | Planner").replace("| draft | - |", f"| {status} | - |")
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
        source = source.replace("| draft | Planner", "| https://github.com/example/repo/issues/10 | Planner").replace("| draft | - |", "| done | - |")
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


class LedgerValidationTests(unittest.TestCase):
    issue = "https://github.com/example/repo/issues/12"

    def document(self, *, issue=None, status="active", changes=None):
        source = spine_text(spine_id="root", spine_type="root", root="self", parent="none")
        original = next(line for line in source.splitlines() if line.startswith("| draft | Planner"))
        header, _ = validate_spine.parse_table(validate_spine.parse_sections(source)["Issue Ledger"])
        values = {
            "Issue": self.issue if issue is None else issue,
            "Role": "Ticket worker", "Owner / Assignment": "worker-12",
            "Title": "Validate command", "Status": status, "Depends On": "none",
            "PR/Branch": "codex/issue-12", "Base": "abc1234",
            "Acceptance": "Tests pass", "Latest Evidence": "Regression suite passed",
            "Last Verified": "2026-09-06", "Next Action": "Manager review",
        }
        values.update(changes or {})
        row = "| " + " | ".join(values[name] for name in header) + " |"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "root.md"
            path.write_text(source.replace(original, row), encoding="utf-8")
            return validate_spine.validate_local(path)

    def test_all_documented_statuses_accept_concrete_issue(self):
        for status in ("draft", "ready", "active", "blocked", "review", "testing", "done", "superseded", "deferred"):
            with self.subTest(status=status):
                self.assertEqual([], self.document(status=status).errors)
        self.assertEqual([], self.document(status="ACTIVE").errors)

    def test_bare_markdown_and_enterprise_issue_urls(self):
        for issue in (
            self.issue,
            f"[#12]({self.issue})",
            self.issue + "#issuecomment-123",
            self.issue + "/?view=compact",
            "https://git.example.internal/team/repo_name/issues/123",
            "[Enterprise issue](https://git.example.internal:8443/team/repo.name/issues/123)",
        ):
            with self.subTest(issue=issue):
                self.assertEqual([], self.document(issue=issue).errors)

    def test_invalid_issue_references_fail(self):
        invalid = (
            "not-a-github-issue", "#12", "", "none", "draft", "<issue URL>",
            "https://github.com/example/repo/pull/12",
            "https://github.com/example/repo/issues", "https://github.com/example/repo/issues/",
            "https://github.com/example/repo/issues/twelve", "https://github.com/example/repo/issues/0",
            "https://github.com/example/repo/issues/-1", "https://github.com/example/repo/issues/12/extra",
            "http://github.com/example/repo/issues/12", "https:///example/repo/issues/12",
            "https://user:password@github.com/example/repo/issues/12",
            "https://github..com/example/repo/issues/12", "https://github.com:99999/example/repo/issues/12",
            "https://github.com/../repo/issues/12", "https://github.com/example/../issues/12",
            f"See {self.issue}", f"[#12]({self.issue}) trailing text",
            "[#12](https://github.com/example/repo/pull/12)",
        )
        for issue in invalid:
            with self.subTest(issue=issue):
                result = self.document(issue=issue)
                self.assertTrue(any("has invalid Issue:" in error for error in result.errors), result.errors)

    def test_non_draft_statuses_cannot_use_draft_reference(self):
        for status in ("ready", "active", "blocked", "review", "testing", "done", "superseded", "deferred"):
            with self.subTest(status=status):
                self.assertTrue(any("has invalid Issue:" in error for error in self.document(issue="draft", status=status).errors))
        self.assertEqual([], self.document(issue="draft", status="draft").errors)

    def test_unknown_statuses_and_real_row_placeholders_fail(self):
        for status in ("", "unknown", "closed", "in progress", "<status>", "active/done"):
            with self.subTest(status=status):
                result = self.document(status=status)
                self.assertTrue(any("has invalid Status:" in error for error in result.errors), result.errors)
        result = self.document(issue="not-an-issue", status="active", changes={"Title": "<title>"})
        self.assertTrue(any("has invalid Issue:" in error for error in result.errors))

    def test_deliberate_draft_template_status_warns(self):
        result = self.document(issue="draft", status="<status>")
        self.assertEqual([], result.errors)
        self.assertIn("ledger row 1 unresolved field: Status", result.warnings)
        result = self.document(issue="draft", status="unknown")
        self.assertTrue(any("has invalid Status:" in error for error in result.errors))

    def test_existing_active_metadata_and_done_evidence_checks_remain(self):
        for column in ("Owner / Assignment", "PR/Branch", "Base", "Last Verified", "Next Action"):
            for status in ("active", "blocked", "review", "testing"):
                with self.subTest(column=column, status=status):
                    result = self.document(status=status, changes={column: ""})
                    self.assertIn(f"ledger row 1 ({self.issue}) is {status} but {column} is empty", result.errors)
        result = self.document(status="done", changes={"Latest Evidence": ""})
        self.assertIn(f"ledger row 1 ({self.issue}) is done without evidence", result.errors)


ROOT = Path(__file__).parents[1]
SCRIPT = VALIDATOR_PATH
validator = validate_spine


class ValidatorCompatibilityTests(unittest.TestCase):
    fixture_dir = ROOT / "tests/fixtures"
    surface_evidence = {
        "browser": "Evidence: real browser on live deployment; one screenshot per step.",
        "cli": "Evidence: exact commands, inputs, exit codes and outputs.",
        "library": "Evidence: runnable consumer example and behavior checks.",
        "infrastructure": "Evidence: authorized health/state probes in the named environment.",
        "documentation": "Evidence: follow instructions, inspect rendered artifacts, links and examples.",
    }

    def source(self, dialect="v2"):
        name = "sprint-v2.md" if dialect == "v2" else "legacy-v1.md"
        return (self.fixture_dir / name).read_text()

    def run_source(self, source, *arguments):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.md"
            path.write_text(source, encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--json", *arguments, str(path)],
                text=True, capture_output=True, check=False,
            )
            return completed.returncode, json.loads(completed.stdout)[0]

    def test_populated_v1_and_v2_fixtures_pass_strict_cli(self):
        for dialect in ("v1", "v2"):
            with self.subTest(dialect=dialect):
                code, result = self.run_source(self.source(dialect), "--strict")
                self.assertEqual(0, code, result)
                self.assertEqual([], result["errors"])
                self.assertEqual([], result["warnings"])

    def test_undeclared_legacy_defaults_to_v1_even_with_strict(self):
        source = self.source("v1").replace("Spine dialect: v1\n", "")
        code, result = self.run_source(source, "--strict", "--dialect", "auto")
        self.assertEqual(0, code, result)
        self.assertEqual([], result["warnings"])

    def test_cli_override_precedes_supported_declaration(self):
        source = self.source("v1")
        code, result = self.run_source(source, "--dialect", "v2", "--strict")
        self.assertEqual(1, code)
        self.assertEqual([], result["errors"])
        self.assertIn("v2 Definition Of Done should have SHIP and HARDEN tiers", result["warnings"])
        self.assertFalse(any("unresolved field:" in message for message in result["warnings"]))
        code, result = self.run_source(source.replace("Spine dialect: v1", "Spine dialect: v2"), "--dialect", "v1", "--strict")
        self.assertEqual(0, code, result)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy.md"
            path.write_text(source)
            self.assertIn("v2 Definition Of Done should have SHIP and HARDEN tiers", validator.validate(path, dialect="v2")["warnings"])

    def test_invalid_declared_dialect_cannot_be_hidden_by_override(self):
        for value in ("v3", ""):
            for override in ("auto", "v1", "v2"):
                with self.subTest(value=value, override=override):
                    source = self.source("v1").replace("Spine dialect: v1", f"Spine dialect: {value}")
                    code, result = self.run_source(source, "--dialect", override)
                    self.assertEqual(1, code)
                    self.assertIn(f"unsupported Spine dialect: {value or '(empty)'}; expected v1 or v2", result["errors"])

    def test_invalid_cli_override_is_usage_error(self):
        completed = subprocess.run([sys.executable, str(SCRIPT), "--dialect", "v3", str(self.fixture_dir / "legacy-v1.md")], text=True, capture_output=True)
        self.assertEqual(2, completed.returncode)
        self.assertIn("invalid choice", completed.stderr)
        result = validator.validate(self.fixture_dir / "legacy-v1.md", dialect="v3")
        self.assertIn("unsupported dialect override: v3; expected auto, v1 or v2", result["errors"])

    def test_missing_v2_contract_warns_and_strict_fails(self):
        source = self.source().replace("HARDEN —", "Later —")
        expected = "v2 Definition Of Done should have SHIP and HARDEN tiers"
        for arguments, expected_code in (((), 0), (("--strict",), 1)):
            code, result = self.run_source(source, *arguments)
            self.assertEqual(expected_code, code)
            self.assertEqual([], result["errors"])
            self.assertEqual([expected], result["warnings"])

    def test_each_surface_requires_its_own_evidence(self):
        for surface, evidence in self.surface_evidence.items():
            with self.subTest(surface=surface):
                source = self.source().replace("Acceptance surface: cli", f"Acceptance surface: {surface}")
                source = source.replace(self.surface_evidence["cli"], evidence)
                code, result = self.run_source(source, "--strict")
                self.assertEqual(0, code, result)
                self.assertEqual([], result["warnings"])
                code, result = self.run_source(source.replace(evidence, "Evidence: pending execution."), "--strict")
                self.assertEqual(1, code)
                self.assertEqual(1, len(result["warnings"]), result)
                self.assertTrue(result["warnings"][0].startswith(f"v2 SHIP journey should state {surface} evidence:"), result)

    def test_personal_execution_remains_required_for_every_surface(self):
        for surface, evidence in self.surface_evidence.items():
            source = self.source().replace("Acceptance surface: cli", f"Acceptance surface: {surface}")
            source = source.replace(self.surface_evidence["cli"], evidence).replace("personally", "automatically")
            code, result = self.run_source(source, "--strict")
            self.assertEqual(1, code)
            self.assertIn("v2 SHIP journey should state the personal execution contract", result["warnings"])

    def test_unknown_and_missing_acceptance_surface(self):
        for value in ("mobile", "cli | mobile", "cli | browser"):
            source = self.source().replace("Acceptance surface: cli", f"Acceptance surface: {value}")
            code, result = self.run_source(source)
            self.assertEqual(1, code)
            self.assertIn(f"unsupported Acceptance surface: {value}; expected browser, cli, library, infrastructure or documentation", result["errors"])
        source = self.source().replace("Acceptance surface: cli\n", "")
        code, result = self.run_source(source, "--strict")
        self.assertEqual(1, code)
        self.assertEqual(["v2 unresolved Acceptance surface: choose browser, cli, library, infrastructure or documentation"], result["warnings"])

    def test_malformed_structure_fails_in_both_dialects(self):
        for dialect in ("v1", "v2"):
            source = self.source(dialect).replace("## Mission", "## Missing Mission")
            code, result = self.run_source(source)
            self.assertEqual(1, code)
            self.assertIn("missing section: Mission", result["errors"])

    def test_current_workflow_contracts_are_enforced(self):
        cases = (
            ("Search scope: current epicspine-skill repository only", "", "v2 discovery missing field: Search scope"),
            ("record adaptations and validation", "record sources", "v2 Ticket-worker role should record reuse adaptations and validation"),
            ("Choose safe reversible options within approved scope and journal uncertainty; required approvals remain gates.", "Choose anything automatically.", "v2 Decisions should constrain defaults to safe reversible choices within approved scope, journal uncertainty, and preserve gates"),
            ("stop dependent work", "keep all work running", "v2 Human Gates should stop dependent work, allow only independent authorized work, and never treat silence as approval"),
        )
        for original, replacement, expected in cases:
            with self.subTest(expected=expected):
                code, result = self.run_source(self.source().replace(original, replacement), "--strict")
                self.assertEqual(1, code)
                self.assertEqual([expected], result["warnings"])

    def test_discovery_values_must_be_resolved_for_strict_v2(self):
        original = self.source()
        values = validator.parse_key_values(validator.parse_sections(original)["Architecture And Context"])
        fields = ("Search scope", "Search budget", "Search evidence", "Method rationale")
        for field in fields:
            for unresolved in ("", "   ", "<fill this>", "tbd"):
                with self.subTest(field=field, unresolved=unresolved):
                    source = original.replace(f"{field}: {values[field]}", f"{field}: {unresolved}")
                    code, result = self.run_source(source, "--strict")
                    self.assertEqual(1, code)
                    self.assertEqual([], result["errors"])
                    self.assertEqual([f"v2 discovery unresolved field: {field}"], result["warnings"])
        source = original
        for field in fields:
            source = source.replace(f"{field}: {values[field]}", f"{field}:")
        code, result = self.run_source(source, "--strict")
        self.assertEqual(1, code)
        self.assertEqual([f"v2 discovery unresolved field: {field}" for field in fields], result["warnings"])
        code, result = self.run_source(source, "--strict", "--dialect", "v1")
        self.assertEqual(0, code, result)

    def test_template_warnings_are_placeholders_not_missing_contracts(self):
        template = (ROOT / "skill/epic-spine/assets/epic-spine-template.md").read_text()
        code, result = self.run_source(template)
        self.assertEqual(0, code, result)
        self.assertEqual([], result["errors"])
        self.assertIn("unresolved field: Repository", result["warnings"])
        self.assertIn("v2 unresolved Acceptance surface: choose browser, cli, library, infrastructure or documentation", result["warnings"])
        self.assertTrue(all("unresolved" in message or message == "Updated still contains a template date" for message in result["warnings"]), result)
        code, result = self.run_source(template, "--strict")
        self.assertEqual(1, code)

    def test_superseded_redirect_warning(self):
        source = self.source().replace("Status: ready", "Status: SUPERSEDED", 1).replace("Execution status: ready", "Execution status: SUPERSEDED")
        code, result = self.run_source(source, "--strict")
        self.assertEqual(1, code)
        self.assertEqual(["SUPERSEDED status should name the replacement and say do not execute"], result["warnings"])


if __name__ == "__main__":
    unittest.main()
