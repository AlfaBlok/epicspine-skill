from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_validate_spine import validate_spine as validator

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skill/epic-spine/scripts/rollup_spine.py"
SPEC = importlib.util.spec_from_file_location("rollup_spine", SCRIPT)
assert SPEC and SPEC.loader
rollup = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rollup
SPEC.loader.exec_module(rollup)

MAP_HEADER = "| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |"
MAP_SEPARATOR = "|---|---|---|---|---|---|---|---|---|"


def write_spine(folder, name, *, parent=None, children=()):
    text = (ROOT / "examples/EPIC-COMPACT-EXAMPLE.md").read_text()
    text = text.replace("Spine ID: synthetic-compact-example", f"Spine ID: {name}")
    text = text.replace("Primary document: EPIC-COMPACT-EXAMPLE.md", f"Primary document: {name}.md")
    text = text.replace("Owner: example-steward", f"Owner: steward-{name}")
    text = text.replace("Evidence: [Synthetic history](EPIC-COMPACT-HISTORY.md#draft-review)", "Evidence: [Acceptance](#definition-of-done)")
    text = text.replace("Integration branch: codex/example", "Integration branch: codex/example\nSpine Type: " + ("branch" if parent else "root") + "\nRoot spine: " + ("[Root](root.md)" if parent else "self") + "\nParent spine: " + (f"[Parent]({parent}.md)" if parent else "none") + "\nAdditional root rationale: n/a")
    rows = [f"| {child} | child | [{child}]({child}.md) | Preserve `purpose-{child}` | ready | none | pending | 2026-09-06 | Previous projection |" for child in children]
    mapping = "\n".join([MAP_HEADER, MAP_SEPARATOR, *rows]) if rows else "No child spines."
    text += "\n## Spine Map\n\n" + mapping + "\n"
    path = folder / f"{name}.md"
    path.write_text(text)
    return path


class ExecutionRollupTests(unittest.TestCase):
    def graph(self, folder, depth=1):
        root = write_spine(folder, "root", children=("child",))
        child = write_spine(folder, "child", parent="root", children=("leaf",) if depth == 2 else ())
        if depth == 2:
            write_spine(folder, "leaf", parent="child")
        return root, child

    def apply(self, plan, **overrides):
        arguments = {"bound_target": Path(plan["target"]), "steward": plan["steward"], "scope_root": Path(plan["scope_root"]), "write_root": Path(plan["scope_root"]), "expected_proposal_hash": rollup.proposal_hash(plan)}
        arguments.update(overrides)
        return rollup.apply_rollup(plan, **arguments)

    def test_preview_is_deterministic_read_only_and_apply_only_projects_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, child = self.graph(folder)
            original_root, original_child = root.read_bytes(), child.read_bytes()
            first = rollup.plan_rollup(root, folder)
            self.assertEqual(first, rollup.plan_rollup(root, folder))
            self.assertTrue(first["changed"])
            self.assertEqual(original_root, root.read_bytes())
            self.assertEqual(original_child, child.read_bytes())
            self.assertIn("Preserve `purpose-child`", first["candidate"])
            self.assertIn("[Acceptance](child.md#definition-of-done)", first["candidate"])
            self.assertEqual("applied", self.apply(first))
            self.assertEqual(original_child, child.read_bytes())
            original_sections = validator.parse_sections(original_root.decode())
            result_sections = validator.parse_sections(root.read_text())
            for section in ("Mission", "Non-Goals", "Current State", "Definition Of Done", "Decisions", "Issue Ledger"):
                self.assertEqual(original_sections[section], result_sections[section])
            self.assertEqual([], validator.validate_local(root).errors)
            self.assertEqual("already-applied", self.apply(first))
            current = rollup.plan_rollup(root, folder)
            self.assertFalse(current["changed"])
            self.assertEqual([], current["problems"])

    def test_changed_child_invalidates_receipt_and_stale_proposals(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, child = self.graph(folder)
            plan = rollup.plan_rollup(root, folder)
            self.apply(plan)
            child.write_text(child.read_text().replace("Status: ready", "Status: done"))
            stale = rollup.plan_rollup(root, folder)
            self.assertTrue(stale["changed"])
            self.assertTrue(any("stale:" in problem for problem in stale["problems"]))
            with self.assertRaisesRegex(ValueError, "child inputs changed"):
                self.apply(plan)
            self.apply(stale)
            self.assertIn("| done |", root.read_text())

    def test_descendant_changes_invalidate_ancestors_without_writing_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, child = self.graph(folder, depth=2)
            self.apply(rollup.plan_rollup(child, folder))
            self.apply(rollup.plan_rollup(root, folder))
            before = root.read_bytes()
            leaf = folder / "leaf.md"
            leaf.write_text(leaf.read_text().replace("Status: ready", "Status: active"))
            ancestor = rollup.plan_rollup(root, folder)
            self.assertTrue(ancestor["changed"])
            self.assertTrue(any("incomplete:" in problem for problem in ancestor["problems"]))
            self.assertEqual(before, root.read_bytes())
            # An out-of-order ancestor receipt must not claim descendant coverage.
            self.apply(ancestor)
            self.assertTrue(rollup.plan_rollup(root, folder)["problems"])
            self.apply(rollup.plan_rollup(child, folder))
            self.assertTrue(rollup.plan_rollup(root, folder)["changed"])
            self.apply(rollup.plan_rollup(root, folder))
            self.assertEqual([], rollup.plan_rollup(root, folder)["problems"])

    def test_missing_conflicting_and_unmanaged_children_are_explicit(self):
        for mode in ("missing", "conflicting", "unmanaged"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                root, child = self.graph(folder)
                if mode == "missing":
                    child.unlink()
                elif mode == "conflicting":
                    child.write_text(child.read_text().replace("Owner: steward-child", "Owner: steward-child\nOwner: another-steward"))
                else:
                    child.write_text(child.read_text().replace("Owner: steward-child\n", ""))
                plan = rollup.plan_rollup(root, folder)
                self.assertIn(mode, plan["candidate"])
                self.assertIn("incomplete", plan["candidate"])
                self.assertTrue(plan["problems"])

    def test_child_root_lineage_must_match_parent(self):
        for declaration in ("[Wrong](wrong.md)", "self", "none", ""):
            with self.subTest(root=declaration), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                root, child = self.graph(folder)
                child.write_text(child.read_text().replace("Root spine: [Root](root.md)", "Root spine: " + declaration))
                plan = rollup.plan_rollup(root, folder)
                self.assertIn("conflicting", plan["candidate"])
                self.assertTrue(any("Root spine disagrees" in problem for item in plan["input_diagnostics"] for problem in item["problems"]))

    def test_apply_requires_matching_authority_target_scope_and_reviewed_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, child = self.graph(folder)
            plan = rollup.plan_rollup(root, folder)
            original = root.read_bytes()
            for override, expected in (
                ({"steward": "not-the-owner"}, "target-steward binding"),
                ({"bound_target": child}, "explicit target binding"),
                ({"scope_root": folder.parent}, "explicit scope binding"),
                ({"expected_proposal_hash": "wrong"}, "proposal hash"),
                ({"write_root": folder / "absent"}, "write root"),
            ):
                with self.subTest(override=override), self.assertRaisesRegex(ValueError, expected):
                    self.apply(plan, **override)
            tampered = dict(plan, candidate=plan["candidate"].replace("## Mission", "## Unauthorized mission"))
            with self.assertRaisesRegex(ValueError, "target or proposal changed"):
                self.apply(tampered)
            root.write_text(root.read_text() + "\nNewer steward decision.\n")
            with self.assertRaisesRegex(ValueError, "target or proposal changed"):
                self.apply(plan)
            self.assertNotEqual(original, root.read_bytes())
            self.assertIn("Newer steward decision.", root.read_text())

    def test_interruption_before_or_after_replace_is_retry_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, _ = self.graph(folder)
            plan = rollup.plan_rollup(root, folder)
            original = root.read_bytes()
            with patch.object(rollup.os, "replace", side_effect=OSError("simulated interruption")):
                with self.assertRaises(OSError):
                    self.apply(plan)
            self.assertEqual(original, root.read_bytes())
            self.assertEqual([], list(folder.glob(".*.rollup-*")))
            replace = rollup.os.replace
            def replace_then_interrupt(source, target):
                replace(source, target)
                raise OSError("acknowledgement lost")
            with patch.object(rollup.os, "replace", side_effect=replace_then_interrupt):
                with self.assertRaises(OSError):
                    self.apply(plan)
            self.assertEqual(plan["candidate"], root.read_text())
            self.assertEqual("already-applied", self.apply(plan))

    def test_scope_limits_and_offline_ticket_verification_are_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, child = self.graph(folder)
            child.write_text(child.read_text().replace("| draft | Ticket worker", "| https://github.com/example/repo/issues/1 | Ticket worker"))
            plan = rollup.plan_rollup(root, folder)
            self.assertIn("github-unverified", plan["candidate"])
            limited = rollup.plan_rollup(root, folder, max_inputs=1)
            self.assertIn("incomplete", limited["candidate"])
            self.assertTrue(limited["problems"])
            root.write_text(root.read_text().replace("(child.md)", "(../outside.md)"))
            escaped = rollup.plan_rollup(root, folder)
            self.assertIn("missing", escaped["candidate"])
            self.assertTrue(escaped["problems"])

    def test_crlf_and_existing_header_markup_remain_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, _ = self.graph(folder)
            root.write_bytes(root.read_bytes().replace(b"| Status |", b"| `Status` |").replace(b"\n", b"\r\n"))
            plan = rollup.plan_rollup(root, folder)
            self.apply(plan)
            self.assertEqual("already-applied", self.apply(plan))
            self.assertFalse(rollup.plan_rollup(root, folder)["changed"])
            self.assertIn("| `Status` |", root.read_text())

    def test_rollup_scope_is_checked_before_any_external_ticket_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, child = self.graph(folder)
            child.write_text(child.read_text().replace("Spine dialect: v1", "Spine dialect: v1\nTicket backend: local\nTicket root: ../external\nTicket permitted root: /explicitly-permitted-but-outside-scope"))
            original_validator = rollup.validate_local
            def validate_scoped(path):
                if path.resolve() == child.resolve():
                    raise AssertionError("backend reader called before rollup scope preflight")
                return original_validator(path)
            with patch.object(rollup, "validate_local", side_effect=validate_scoped):
                plan = rollup.plan_rollup(root, folder)
            self.assertIn("missing", plan["candidate"])
            self.assertIn("incomplete", plan["candidate"])

    def test_malformed_or_nontrailing_receipts_are_never_silently_repaired(self):
        for suffix in (rollup.START + "{}" + rollup.END, rollup.START + "not-json", rollup.START + '{"version":1,"inputs":[],"fingerprint":"x"}' + rollup.END + "\nSteward decision after receipt."):
            with tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                root, _ = self.graph(folder)
                root.write_text(root.read_text() + "\n" + suffix)
                original = root.read_bytes()
                with self.assertRaises(ValueError):
                    rollup.plan_rollup(root, folder)
                self.assertEqual(original, root.read_bytes())

    def test_reference_style_projected_links_are_refused_without_source_rewrite(self):
        for reference in ("[review evidence][proof]", "[proof]"):
            with tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                root, child = self.graph(folder)
                child.write_text(child.read_text().replace("Evidence: [Acceptance](#definition-of-done)", f"Evidence: {reference}") + "\n[proof]: https://example.com/proof\n")
                original = root.read_bytes()
                with self.assertRaisesRegex(ValueError, "reference.*links in projected state"):
                    rollup.plan_rollup(root, folder)
                self.assertEqual(original, root.read_bytes())

    def test_check_and_preview_cli_do_not_mutate_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            root, _ = self.graph(folder)
            original = root.read_bytes()
            checked = subprocess.run([sys.executable, "-B", str(SCRIPT), "check", str(root), "--scope-root", str(folder)], capture_output=True, text=True)
            self.assertEqual(1, checked.returncode)
            preview = subprocess.run([sys.executable, "-B", str(SCRIPT), "preview", str(root), "--scope-root", str(folder)], capture_output=True, text=True)
            self.assertEqual(0, preview.returncode, preview.stderr)
            self.assertIn("Proposal SHA256:", preview.stdout)
            self.assertIn("--- ", preview.stdout)
            self.assertEqual(original, root.read_bytes())


if __name__ == "__main__":
    unittest.main()
