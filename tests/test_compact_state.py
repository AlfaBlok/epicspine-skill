from __future__ import annotations

import hashlib
import importlib.util
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_validate_spine import validate_spine as validator

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "skill/epic-spine/scripts"
SPEC = importlib.util.spec_from_file_location("migrate_spine", SCRIPTS / "migrate_spine.py")
assert SPEC and SPEC.loader
migration = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = migration
SPEC.loader.exec_module(migration)


class CompactStateTests(unittest.TestCase):
    def source(self):
        return (ROOT / "examples/EPIC-COMPACT-EXAMPLE.md").read_text()

    def document(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "epic.md"
            path.write_text(text)
            return validator.validate_local(path)

    def test_compact_example_has_one_resolved_state_without_optional_hierarchy(self):
        document = self.document(self.source())
        self.assertEqual([], document.errors)
        self.assertEqual([], document.warnings)
        self.assertEqual("example-steward", document.state["owner"])
        self.assertEqual("none", document.state["waiting_on"])
        self.assertEqual("Run the validator against this file.", document.state["next_action"])
        self.assertNotIn("phase", document.state)
        self.assertTrue(document.state_sources["owner"][0].startswith("Current State / Owner (line "))
        validator.validate_graph([document])
        # Temporary source no longer exists, so use a real path to test graph mode.
        document = validator.validate_local(ROOT / "examples/EPIC-COMPACT-EXAMPLE.md")
        validator.validate_graph([document])
        self.assertIn("graph validation requires explicit hierarchy fields for compact spines; lineage is undeclared", document.errors)

    def test_declared_compact_hierarchy_is_checked(self):
        text = self.source().replace("Integration branch: codex/example", "Integration branch: codex/example\nSpine Type: root\nRoot spine: self\nParent spine: none\nAdditional root rationale: n/a")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "root.md"
            path.write_text(text)
            document = validator.validate_local(path)
            validator.validate_graph([document])
            self.assertEqual([], document.errors)
        document = self.document(text.replace("Root spine: self", "Root spine: none"))
        self.assertIn("root spine must declare Root spine: self", document.errors)

    def test_required_state_missing_empty_and_placeholder_values_fail(self):
        original = self.source()
        for label, key in validator.STATE_FIELDS.items():
            value = validator.parse_key_values(validator.parse_sections(original)["Current State"])[label]
            with self.subTest(label=label):
                document = self.document(original.replace(f"{label}: {value}\n", ""))
                self.assertIn(f"Current State missing field: {label}", document.errors)
                for unresolved in ("", "<fill this>"):
                    document = self.document(original.replace(f"{label}: {value}", f"{label}: {unresolved}"))
                    self.assertIn(f"Current State unresolved field: {label}", document.errors)

    def test_alias_conflicts_never_choose_a_winner(self):
        text = self.source().replace("Waiting on: none", "Waiting on: none\nBlocker: approval required")
        document = self.document(text)
        self.assertTrue(any("conflicting state waiting_on:" in error for error in document.errors))
        self.assertNotIn("waiting_on", document.state)
        self.assertEqual(2, len(document.state_sources["waiting_on"]))
        document = self.document(self.source().replace("Waiting on: none", "Blockers: nothing"))
        self.assertEqual([], document.errors)
        self.assertEqual("none", document.state["waiting_on"])

    def test_compact_rejects_competing_legacy_fields_even_when_equal(self):
        text = self.source().replace("Spine profile: compact", "Spine profile: compact\nActive spine steward: example-steward")
        document = self.document(text)
        self.assertTrue(any("competing compact state: preamble / Active spine steward" in error for error in document.errors))
        text = self.source() + "\n## Execution Cursor\n\nNext action: Run the validator against this file.\n"
        document = self.document(text)
        self.assertTrue(any("competing compact state: Execution Cursor / Next action" in error for error in document.errors))

    def test_legacy_consistent_and_conflicting_sources(self):
        original = (ROOT / "tests/fixtures/legacy-v1.md").read_text()
        document = self.document(original)
        self.assertEqual([], document.errors)
        self.assertEqual("Run validation.", document.state["next_action"])
        self.assertEqual(2, len(document.state_sources["next_action"]))
        document = self.document(original.replace("Next action: Run validation.", "Next action: Ship immediately.", 1))
        self.assertTrue(any("conflicting state next_action:" in error and "Current State" in error and "Execution Cursor" in error for error in document.errors))
        self.assertNotIn("next_action", document.state)
        document = self.document(original.replace("Execution status: ready", "Execution status: active"))
        self.assertTrue(any("conflicting state status:" in error for error in document.errors))

    def test_no_approved_work_is_an_explicit_valid_gate(self):
        document = self.document(self.source().replace("Approved work: Read and validate this synthetic example locally.", "Approved work: none"))
        self.assertEqual([], document.errors)
        self.assertEqual("none", document.state["approved_work"])

    def test_duplicate_state_sections_and_literal_pipe_conflicts_fail(self):
        text = self.source() + "\n## Current State\n\nResult: contradictory | evidence\n"
        document = self.document(text)
        self.assertIn("duplicate state section: Current State", document.errors)
        self.assertTrue(any("conflicting state result:" in error for error in document.errors))


class MigrationTests(unittest.TestCase):
    fixture = ROOT / "tests/fixtures/legacy-migration.md"

    def setup_source(self, folder):
        path = folder / "legacy-migration.md"
        path.write_bytes(self.fixture.read_bytes().replace(b"\n", b"\r\n"))
        return path

    def test_preview_is_read_only_and_apply_preserves_bytes_links_and_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = self.setup_source(folder)
            original = path.read_bytes()
            completed = subprocess.run([sys.executable, "-B", str(SCRIPTS / "migrate_spine.py"), str(path)], text=True, capture_output=True)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("Source SHA256:", completed.stdout)
            self.assertIn("--- ", completed.stdout)
            self.assertEqual(original, path.read_bytes())
            self.assertEqual([path], list(folder.iterdir()))
            plan = migration.plan_migration(path)
            migration.apply_migration(plan, hashlib.sha256(original).hexdigest())
            self.assertEqual(original, plan.archive.read_bytes())
            self.assertEqual(path.resolve().parent, plan.archive.parent)
            self.assertEqual([], validator.validate_local(path).errors)
            after = path.read_text()
            self.assertIn("Spine ID: synthetic-migration", after)
            self.assertIn("| rejected | Use the connected hierarchy", after)
            self.assertIn("[H-001](#draft-review)", after)
            self.assertIn('<a id="draft-review"></a>', after)
            self.assertIn('<a id="old-evidence"></a>', after)
            self.assertIn(f"{plan.archive.name}#handoff-journal", after)
            self.assertIn(f"{plan.archive.name}#draft-review", after)
            self.assertIn("[relative source](legacy-v1.md)", plan.archive.read_text())
            self.assertNotIn("Historical synthetic handoff with ID H-001", after)
            original_fragments = {migration.anchor(name) for name in re.findall(r"(?m)^#{1,6} (.+?)\r?$", original.decode())}
            current_fragments = {migration.anchor(name) for name in re.findall(r"(?m)^#{1,6} (.+?)$", after)}
            current_fragments.update(re.findall(r'<a id="([^"]+)"', after))
            self.assertTrue(original_fragments.issubset(current_fragments), original_fragments - current_fragments)
            self.assertNotIn("Execution Cursor", validator.parse_sections(after))

    def test_conflicts_and_missing_required_data_stop_migration(self):
        for old, new in (("Execution status: ready", "Execution status: blocked"), ("Last verified: 2026-09-06T14:00:00Z", ""), ("## Non-Goals", "## Other Scope")):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "source.md"
                path.write_text(self.fixture.read_text().replace(old, new))
                original = path.read_bytes()
                with self.assertRaises(ValueError):
                    migration.plan_migration(path)
                self.assertEqual(original, path.read_bytes())

    def test_ambiguous_old_fragments_require_manual_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.md"
            path.write_text(self.fixture.read_text() + "\n### Draft review\nDuplicate history heading.\n")
            with self.assertRaisesRegex(ValueError, "ambiguous heading anchors"):
                migration.plan_migration(path)

    def test_heading_link_markup_is_refused_without_changing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.md"
            original = self.fixture.read_text().replace("### Draft review", "### [Draft review](legacy-v1.md)")
            source.write_text(original)
            with self.assertRaisesRegex(ValueError, "heading link/reference markup requires manual migration"):
                migration.plan_migration(source)
            self.assertEqual(original, source.read_text())
            self.assertEqual([source], list(Path(tmp).iterdir()))

    def test_reference_definitions_in_archived_sections_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.md"
            original = self.fixture.read_text().replace("- [ ] Graph validation passes.", "- [ ] Read [review evidence][proof].")
            original = original.replace("## Handoff Journal", "## Handoff Journal\n\n[proof]: https://github.com/example/repo/issues/1")
            source.write_text(original)
            with self.assertRaisesRegex(ValueError, "Markdown reference definitions require manual migration"):
                migration.plan_migration(source)
            self.assertEqual(original, source.read_text())
            self.assertEqual([source], list(Path(tmp).iterdir()))

    def test_apply_requires_reviewed_hash_and_refuses_stale_source_or_archive_clobber(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.setup_source(Path(tmp))
            plan = migration.plan_migration(path)
            with self.assertRaisesRegex(ValueError, "expected source hash differs"):
                migration.apply_migration(plan, "wrong")
            completed = subprocess.run([sys.executable, "-B", str(SCRIPTS / "migrate_spine.py"), str(path), "--apply"], capture_output=True, text=True)
            self.assertEqual(1, completed.returncode)
            self.assertIn("--apply requires --expect-sha256", completed.stderr)
            path.write_bytes(plan.original + b"\nNewer work\n")
            with self.assertRaisesRegex(ValueError, "source changed"):
                migration.apply_migration(plan, plan.source_sha256)
            self.assertFalse(plan.archive.exists())
            path.write_bytes(plan.original)
            plan.archive.write_bytes(b"Existing history")
            with self.assertRaisesRegex(ValueError, "existing archive differs"):
                migration.apply_migration(plan, plan.source_sha256)
            self.assertEqual(b"Existing history", plan.archive.read_bytes())
            self.assertEqual(plan.original, path.read_bytes())
            plan.archive.write_bytes(plan.original)
            migration.apply_migration(plan, plan.source_sha256)
            self.assertEqual(plan.original, plan.archive.read_bytes())
            self.assertTrue(validator.is_history_snapshot(plan.archive))
            archive_document = validator.validate_local(plan.archive)
            active_document = validator.validate_local(path)
            validator.validate_graph([archive_document, active_document])
            self.assertIn("historical snapshot is not an active spine; exclude it from active/graph inventory", archive_document.errors)
            self.assertFalse(any("duplicate Spine ID" in error for doc in (archive_document, active_document) for error in doc.errors))


if __name__ == "__main__":
    unittest.main()
