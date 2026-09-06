from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from test_validate_spine import validate_spine as validator

ROOT = Path(__file__).parents[1]


class TicketBackendTests(unittest.TestCase):
    def setup_local(self, folder):
        target = folder / "research"
        shutil.copytree(ROOT / "examples/local-research", target)
        return target / "EPIC-LOCAL-RESEARCH.md"

    def test_local_records_come_from_files_with_stable_identity_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.setup_local(Path(tmp))
            document = validator.validate_local(source)
            self.assertEqual([], document.errors)
            self.assertEqual([], document.warnings)
            self.assertEqual(2, len(document.tickets))
            record = document.tickets[0]
            self.assertEqual("local:R-001", record["identity"])
            self.assertEqual("ready", record["status"])
            self.assertEqual("example-researcher", record["owner"])
            self.assertEqual("[Protocol draft](../protocol.md#protocol-draft)", record["evidence"])
            self.assertEqual("local-read", record["verification"])
            self.assertEqual("unknown", record["freshness"])
            self.assertEqual("sha256:" + hashlib.sha256(Path(record["location"]).read_bytes()).hexdigest(), record["source_revision"])
            ticket = source.parent / "tickets/R-001.md"
            ticket.write_text(ticket.read_text().replace("Status: ready", "Status: blocked\nWaiting on: protocol approval"))
            changed = validator.validate_local(source)
            self.assertEqual("blocked", changed.tickets[0]["status"])
            self.assertEqual("protocol approval", changed.tickets[0]["waiting_on"])
            self.assertNotEqual(record["source_revision"], changed.tickets[0]["source_revision"])
            self.assertNotIn("protocol approval", source.read_text())

    def test_github_is_default_offline_and_retains_snapshot_uncertainty(self):
        with patch("socket.create_connection", side_effect=AssertionError("unexpected network call")):
            explicit = validator.validate_local(ROOT / "examples/EPIC-GITHUB-TICKETS.md")
            default = validator.validate_local(ROOT / "tests/fixtures/legacy-v1.md")
        self.assertEqual([], explicit.errors)
        self.assertEqual([], default.errors)
        self.assertEqual(explicit.tickets, default.tickets)
        record = explicit.tickets[0]
        self.assertEqual("github:https://github.com/example/repo/issues/1", record["identity"])
        self.assertEqual("https://github.com/example/repo/issues/1", record["location"])
        self.assertEqual("unverified", record["verification"])
        self.assertEqual("unknown", record["freshness"])
        self.assertEqual("", record["source_revision"])
        self.assertEqual("2026-08-16 12:00 UTC", record["declared_verified_at"])

    def test_unknown_backend_and_missing_root_are_diagnosed(self):
        for original, replacement, expected in (
            ("Ticket backend: local", "Ticket backend: other", "unsupported Ticket backend"),
            ("Ticket root: tickets", "Ticket root:", "requires a resolved Ticket root"),
            ("Ticket root: tickets", "Ticket root: missing", "not an existing directory"),
        ):
            with tempfile.TemporaryDirectory() as tmp:
                source = self.setup_local(Path(tmp))
                source.write_text(source.read_text().replace(original, replacement))
                result = validator.validate_local(source)
                self.assertTrue(any(expected in error for error in result.errors), result.errors)

    def test_local_ledger_cannot_duplicate_mutable_ticket_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.setup_local(Path(tmp))
            text = source.read_text().replace("| Ticket | Depends On |", "| Ticket | Depends On | Status |")
            text = text.replace("|---|---|", "|---|---|---|").replace("| [R-001](tickets/R-001.md) | none |", "| [R-001](tickets/R-001.md) | none | done |").replace("| [R-002](tickets/R-002.md) | R-001 |", "| [R-002](tickets/R-002.md) | R-001 | done |")
            source.write_text(text)
            result = validator.validate_local(source)
            self.assertTrue(any("references/dependencies only" in error and "Status" in error for error in result.errors))
            self.assertEqual("ready", result.tickets[0]["status"])

    def test_missing_files_placeholders_and_url_references_fail(self):
        for target in ("tickets/missing.md", "<ticket>", "draft", "https://example.com/ticket.md", "tickets/R-001.md#section", "tickets/R-001.md?q=1", "http://[", "tickets/%00.md"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                source = self.setup_local(Path(tmp))
                source.write_text(source.read_text().replace("tickets/R-001.md", target))
                result = validator.validate_local(source)
                self.assertTrue(any("local ledger row 1" in error for error in result.errors), result.errors)

    def test_local_required_metadata_invalid_status_and_duplicate_fields_fail(self):
        for original, replacement, expected in (
            ("Ticket ID: R-001", "Ticket ID:", "unresolved field: Ticket ID"),
            ("Ticket ID: R-001", "Ticket ID: 123", "invalid Ticket ID"),
            ("Status: ready", "Status: closed", "invalid Status: closed"),
            ("Owner: example-researcher", "Owner: <owner>", "unresolved field: Owner"),
            ("Evidence: [Protocol draft](../protocol.md#protocol-draft)", "Evidence:", "unresolved field: Evidence"),
            ("Status: ready", "Status: ready\nStatus: done", "duplicate field: Status"),
        ):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as tmp:
                source = self.setup_local(Path(tmp))
                ticket = source.parent / "tickets/R-001.md"
                ticket.write_text(ticket.read_text().replace(original, replacement))
                result = validator.validate_local(source)
                self.assertTrue(any(expected in error for error in result.errors), result.errors)
                self.assertFalse(any(record["identity"] == "local:R-001" for record in result.tickets))

    def test_duplicate_ids_and_unresolved_dependencies_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.setup_local(Path(tmp))
            ticket = source.parent / "tickets/R-002.md"
            ticket.write_text(ticket.read_text().replace("Ticket ID: R-002", "Ticket ID: R-001"))
            result = validator.validate_local(source)
            self.assertTrue(any("duplicate ticket identity local:R-001" in error for error in result.errors))
            self.assertEqual([], result.tickets)
        with tempfile.TemporaryDirectory() as tmp:
            source = self.setup_local(Path(tmp))
            source.write_text(source.read_text().replace("| R-001 |", "| R-999 |"))
            result = validator.validate_local(source)
            self.assertTrue(any("unresolved dependency Ticket ID: R-999" in error for error in result.errors))

    def test_root_escape_requires_explicit_bounded_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = self.setup_local(folder)
            moved = folder / "external-tickets"
            shutil.move(source.parent / "tickets", moved)
            text = source.read_text().replace("Ticket root: tickets", "Ticket root: ../external-tickets").replace("(tickets/", "(../external-tickets/")
            source.write_text(text)
            result = validator.validate_local(source)
            self.assertTrue(any("Ticket root escapes the checkout" in error for error in result.errors))
            source.write_text(text.replace("Ticket root: ../external-tickets", f"Ticket root: ../external-tickets\nTicket permitted root: {moved}"))
            result = validator.validate_local(source)
            self.assertEqual([], result.errors)
            source.write_text(source.read_text().replace(str(moved), "/"))
            result = validator.validate_local(source)
            self.assertTrue(any("bounded below the filesystem root" in error for error in result.errors))

    def test_reference_traversal_and_symlink_escapes_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.setup_local(Path(tmp))
            outside = source.parent / "outside.md"
            outside.write_bytes((source.parent / "tickets/R-001.md").read_bytes())
            for target in ("tickets/../outside.md", "tickets/%2e%2e/outside.md", str(outside.resolve())):
                text = source.read_text().replace("tickets/R-001.md", target)
                fields, sections = validator.parse_fields(text), validator.parse_sections(text)
                _, errors = validator.read_tickets(source, fields, sections)
                self.assertTrue(any("escapes Ticket root" in error or "requires a relative Ticket path" in error for error in errors), errors)
            (source.parent / "tickets/link.md").symlink_to(outside)
            source.write_text(source.read_text().replace("tickets/R-001.md", "tickets/link.md"))
            result = validator.validate_local(source)
            self.assertTrue(any("escapes Ticket root" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
