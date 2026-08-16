#!/usr/bin/env python3
"""Validate the local document and connected-graph contracts of EpicSpines."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


REQUIRED_FIELDS = (
    "Status",
    "Updated",
    "Repository",
    "Primary document",
    "Spine ID",
    "Spine Type",
    "Root spine",
    "Parent spine",
    "Additional root rationale",
    "Integration branch",
    "Active spine steward",
    "Last reconciled commit",
)

REQUIRED_SECTIONS = (
    "Role Bindings",
    "Write Scope",
    "Authority By Artifact",
    "Spine Map",
    "Mission",
    "Definition Of Done",
    "Current State",
    "Execution Cursor",
    "Bootstrap Map",
    "Decisions",
    "Issue Ledger",
    "Branch And Integration",
    "Human Gates",
    "Recovery And Takeover",
    "Validation Evidence",
    "Handoff Journal",
    "Open Questions",
)

REQUIRED_CURSOR_FIELDS = (
    "Last attempted",
    "Result",
    "Execution status",
    "Waiting on",
    "Approved work",
    "Next action",
)

REQUIRED_SPINE_MAP_COLUMNS = (
    "Spine ID",
    "Relationship",
    "Spine",
    "Purpose",
    "Status",
    "Health / Blocker",
    "Latest Evidence",
    "Last Rolled Up",
    "Next Action",
)

REQUIRED_DECISION_COLUMNS = (
    "Date",
    "Outcome",
    "Decision / Attempt",
    "Durable Summary",
    "Evidence",
    "Revisit When",
)

REQUIRED_LEDGER_COLUMNS = (
    "Issue",
    "Role",
    "Owner / Assignment",
    "Title",
    "Status",
    "PR/Branch",
    "Base",
    "Latest Evidence",
    "Last Verified",
    "Next Action",
)

ACTIVE_STATUSES = {"active", "blocked", "review", "testing"}
DECISION_OUTCOMES = {"accepted", "rejected", "superseded"}
EMPTY_VALUES = {"", "-", "none", "n/a", "tbd", "<sha>", "<task/thread/agent>"}


@dataclass
class SpineDocument:
    path: Path
    fields: dict[str, str]
    sections: dict[str, str]
    errors: list[str]
    warnings: list[str]

    @property
    def spine_id(self) -> str:
        return normalize(self.fields.get("Spine ID", ""))

    @property
    def spine_type(self) -> str:
        return normalize(self.fields.get("Spine Type", "")).lower()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("`"))


def parse_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^## (.+?)\s*$", text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[normalize(match.group(1))] = text[match.end() : end].strip()
    return sections


def parse_key_values(text: str) -> dict[str, str]:
    return {
        normalize(match.group(1)): normalize(match.group(2))
        for match in re.finditer(r"(?m)^([A-Za-z][A-Za-z ]+):\s*(.*?)\s*$", text)
        if normalize(match.group(2))
    }


def parse_fields(text: str) -> dict[str, str]:
    first_section = re.search(r"(?m)^## ", text)
    preamble = text[: first_section.start()] if first_section else text
    return parse_key_values(preamble)


def parse_table(section: str) -> tuple[list[str], list[list[str]]]:
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return [], []

    def cells(line: str) -> list[str]:
        return [normalize(cell) for cell in line.strip("|").split("|")]

    header = cells(lines[0])
    rows = []
    for line in lines[2:]:
        row = cells(line)
        if len(row) == len(header):
            rows.append(row)
    return header, rows


def is_empty(value: str) -> bool:
    normalized = normalize(value)
    return normalized.lower() in EMPTY_VALUES or normalized.startswith("<")


def is_none(value: str) -> bool:
    return normalize(value).lower() in {"none", "n/a", "-"}


def markdown_target(value: str) -> str | None:
    match = re.search(r"\[[^\]]+\]\(([^)]+)\)", value)
    return unquote(match.group(1)).split("#", 1)[0] if match else None


def resolve_local_link(source: Path, value: str) -> Path | None:
    target = markdown_target(value)
    if target is None:
        candidate = normalize(value).split("#", 1)[0]
        if candidate.lower() in {"", "none", "n/a", "self", "-"} or "://" in candidate:
            return None
        target = candidate
    if "://" in target or target.startswith("#"):
        return None
    path = Path(target)
    return (path if path.is_absolute() else source.parent / path).resolve()


def table_rows(section: str) -> list[dict[str, str]]:
    header, rows = parse_table(section)
    return [dict(zip(header, row)) for row in rows]


def validate_local(path: Path) -> SpineDocument:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.is_file():
        return SpineDocument(path, {}, {}, ["file not found"], [])

    text = path.read_text(encoding="utf-8")
    fields = parse_fields(text)
    sections = parse_sections(text)

    for field in REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"missing field: {field}")
        elif is_empty(fields[field]) and field not in {"Parent spine", "Additional root rationale"}:
            warnings.append(f"unresolved field: {field}")

    for section in REQUIRED_SECTIONS:
        if section not in sections:
            errors.append(f"missing section: {section}")

    spine_type = normalize(fields.get("Spine Type", "")).lower()
    root_spine = normalize(fields.get("Root spine", "")).lower()
    parent_spine = normalize(fields.get("Parent spine", "")).lower()
    if spine_type and spine_type not in {"root", "branch"} and not spine_type.startswith("<"):
        errors.append("Spine Type must be root or branch")
    elif spine_type == "root":
        if root_spine != "self":
            errors.append("root spine must declare Root spine: self")
        if parent_spine != "none":
            errors.append("root spine must declare Parent spine: none")
    elif spine_type == "branch":
        if root_spine in {"", "self", "none", "n/a"} or root_spine.startswith("<"):
            errors.append("branch spine must link to its root spine")
        if parent_spine in {"", "self", "none", "n/a"} or parent_spine.startswith("<"):
            errors.append("branch spine must link to its direct parent spine")
        if root_spine and markdown_target(fields.get("Root spine", "")) is None:
            warnings.append("branch Root spine should be a Markdown link for navigation and graph validation")
        if parent_spine and markdown_target(fields.get("Parent spine", "")) is None:
            warnings.append("branch Parent spine should be a Markdown link for navigation and graph validation")

    cursor = parse_key_values(sections.get("Execution Cursor", ""))
    for field in REQUIRED_CURSOR_FIELDS:
        if field not in cursor:
            errors.append(f"Execution Cursor missing field: {field}")
        elif is_empty(cursor[field]):
            warnings.append(f"Execution Cursor unresolved field: {field}")

    spine_map = sections.get("Spine Map", "")
    if "No child spines." not in spine_map:
        header, rows = parse_table(spine_map)
        if not header:
            errors.append("Spine Map must contain a direct-child table or 'No child spines.'")
        else:
            for column in REQUIRED_SPINE_MAP_COLUMNS:
                if column not in header:
                    errors.append(f"Spine Map missing column: {column}")
            for row_number, row in enumerate(rows, start=1):
                values = dict(zip(header, row))
                relationship = values.get("Relationship", "").lower()
                if relationship and relationship != "child" and not relationship.startswith("<"):
                    errors.append(f"Spine Map row {row_number} Relationship must be child")
                for column in ("Spine ID", "Spine", "Purpose", "Status", "Health / Blocker", "Last Rolled Up", "Next Action"):
                    if column in values and is_empty(values[column]):
                        warnings.append(f"Spine Map row {row_number} unresolved field: {column}")

    decisions = sections.get("Decisions", "")
    decision_header, decision_rows = parse_table(decisions)
    if not decision_header:
        errors.append("Decisions has no Markdown table")
    else:
        for column in REQUIRED_DECISION_COLUMNS:
            if column not in decision_header:
                errors.append(f"Decisions missing column: {column}")
        decision_positions = {name: index for index, name in enumerate(decision_header)}
        if "Outcome" in decision_positions:
            for row_number, row in enumerate(decision_rows, start=1):
                outcome = row[decision_positions["Outcome"]].lower()
                if outcome not in DECISION_OUTCOMES and not outcome.startswith("<"):
                    errors.append(f"decision row {row_number} has invalid Outcome: {outcome}")
                if outcome in {"rejected", "superseded"}:
                    for column in ("Durable Summary", "Evidence", "Revisit When"):
                        if column in decision_positions and is_empty(row[decision_positions[column]]):
                            errors.append(f"decision row {row_number} is {outcome} but {column} is empty")

    ledger = sections.get("Issue Ledger", "")
    header, rows = parse_table(ledger)
    if not header:
        errors.append("Issue Ledger has no Markdown table")
    else:
        for column in REQUIRED_LEDGER_COLUMNS:
            if column not in header:
                errors.append(f"Issue Ledger missing column: {column}")

        positions = {name: index for index, name in enumerate(header)}
        active_fields = ("Issue", "Owner / Assignment", "Status", "PR/Branch", "Base", "Latest Evidence", "Last Verified", "Next Action")
        if all(name in positions for name in active_fields):
            for row_number, row in enumerate(rows, start=1):
                status = row[positions["Status"]].lower()
                issue = row[positions["Issue"]]
                if status in ACTIVE_STATUSES:
                    for column in ("Owner / Assignment", "PR/Branch", "Base", "Last Verified", "Next Action"):
                        if is_empty(row[positions[column]]):
                            errors.append(f"ledger row {row_number} ({issue}) is {status} but {column} is empty")
                if status == "done" and is_empty(row[positions["Latest Evidence"]]):
                    errors.append(f"ledger row {row_number} ({issue}) is done without evidence")

    if "YYYY-MM-DD" in fields.get("Updated", ""):
        warnings.append("Updated still contains a template date")

    return SpineDocument(path.resolve(), fields, sections, errors, warnings)


def validate_graph(documents: list[SpineDocument]) -> None:
    existing = [doc for doc in documents if doc.path.is_file()]
    by_path = {doc.path: doc for doc in existing}
    by_id: dict[str, SpineDocument] = {}
    for doc in existing:
        if is_empty(doc.spine_id):
            continue
        if doc.spine_id in by_id:
            doc.errors.append(f"duplicate Spine ID also used by {by_id[doc.spine_id].path}")
            by_id[doc.spine_id].errors.append(f"duplicate Spine ID also used by {doc.path}")
        else:
            by_id[doc.spine_id] = doc

    roots = [doc for doc in existing if doc.spine_type == "root"]
    if len(roots) > 1:
        canonical = [doc for doc in roots if is_none(doc.fields.get("Additional root rationale", ""))]
        if len(canonical) != 1:
            paths = ", ".join(str(doc.path) for doc in roots)
            for doc in roots:
                doc.errors.append(
                    "a multi-root graph must have exactly one canonical root with "
                    f"Additional root rationale: n/a; roots: {paths}"
                )

    def require_graph_target(doc: SpineDocument, field: str) -> SpineDocument | None:
        target = resolve_local_link(doc.path, doc.fields.get(field, ""))
        if target is None:
            doc.errors.append(f"graph validation requires a local Markdown link for {field}")
            return None
        target_doc = by_path.get(target)
        if target_doc is None:
            doc.errors.append(f"{field} target is not included in graph validation: {target}")
        return target_doc

    for doc in existing:
        if doc.spine_type != "branch":
            continue
        parent = require_graph_target(doc, "Parent spine")
        declared_root = require_graph_target(doc, "Root spine")
        if parent is not None and parent.path == doc.path:
            doc.errors.append("spine cannot be its own parent")
        if declared_root is not None and declared_root.spine_type != "root":
            doc.errors.append(f"declared Root spine is not type root: {declared_root.path}")

        if parent is not None:
            registrations = table_rows(parent.sections.get("Spine Map", ""))
            matches = []
            for row in registrations:
                row_target = resolve_local_link(parent.path, row.get("Spine", ""))
                if row.get("Spine ID") == doc.spine_id or row_target == doc.path:
                    matches.append((row, row_target))
            if not matches:
                doc.errors.append(f"parent does not reciprocally register this branch in Spine Map: {parent.path}")
            else:
                row, row_target = matches[0]
                if row.get("Spine ID") != doc.spine_id:
                    doc.errors.append(f"parent Spine Map uses wrong Spine ID for this branch: {row.get('Spine ID')}")
                if row_target != doc.path:
                    doc.errors.append("parent Spine Map link does not resolve to this branch")

        seen = {doc.path}
        cursor = parent
        computed_root: SpineDocument | None = None
        while cursor is not None:
            if cursor.path in seen:
                doc.errors.append(f"parent cycle detected through {cursor.path}")
                break
            seen.add(cursor.path)
            if cursor.spine_type == "root":
                computed_root = cursor
                break
            if cursor.spine_type != "branch":
                break
            cursor_path = resolve_local_link(cursor.path, cursor.fields.get("Parent spine", ""))
            cursor = by_path.get(cursor_path) if cursor_path else None
        if computed_root is not None and declared_root is not None and computed_root.path != declared_root.path:
            doc.errors.append(
                f"declared root {declared_root.path} disagrees with parent-chain root {computed_root.path}"
            )

    for parent in existing:
        for row in table_rows(parent.sections.get("Spine Map", "")):
            if row.get("Relationship", "").lower() != "child":
                continue
            child_path = resolve_local_link(parent.path, row.get("Spine", ""))
            if child_path is None:
                parent.errors.append(f"graph validation requires local child link for Spine ID {row.get('Spine ID', '?')}")
                continue
            child = by_path.get(child_path)
            if child is None:
                parent.errors.append(f"child target is not included in graph validation: {child_path}")
                continue
            declared_parent = resolve_local_link(child.path, child.fields.get("Parent spine", ""))
            if declared_parent != parent.path:
                parent.errors.append(f"child {child.path} does not point back to this parent")


def result_for(doc: SpineDocument) -> dict[str, object]:
    return {"path": str(doc.path), "errors": doc.errors, "warnings": doc.warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument(
        "--graph",
        action="store_true",
        help="Validate local parent/root links, reciprocal registration, cycles, IDs, and multiple roots across all paths",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable results")
    args = parser.parse_args()

    documents = [validate_local(path) for path in args.paths]
    if args.graph:
        validate_graph(documents)

    results = [result_for(doc) for doc in documents]
    exit_code = 0
    for result in results:
        if result["errors"] or (args.strict and result["warnings"]):
            exit_code = 1

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            print(result["path"])
            for error in result["errors"]:
                print(f"  ERROR: {error}")
            for warning in result["warnings"]:
                print(f"  WARN: {warning}")
            if not result["errors"] and not result["warnings"]:
                print("  OK")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
