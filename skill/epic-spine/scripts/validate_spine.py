#!/usr/bin/env python3
"""Validate the structural contracts of an EpicSpine Markdown document."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = (
    "Status",
    "Updated",
    "Repository",
    "Primary document",
    "Integration branch",
    "Active spine steward",
    "Last reconciled commit",
)

REQUIRED_SECTIONS = (
    "Role Bindings",
    "Write Scope",
    "Authority By Artifact",
    "Mission",
    "Definition Of Done",
    "Current State",
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
EMPTY_VALUES = {"", "-", "none", "n/a", "tbd", "<sha>", "<task/thread/agent>"}


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("`"))


def parse_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^## (.+?)\s*$", text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[normalize(match.group(1))] = text[match.end() : end].strip()
    return sections


def parse_fields(text: str) -> dict[str, str]:
    first_section = re.search(r"(?m)^## ", text)
    preamble = text[: first_section.start()] if first_section else text
    return {
        normalize(match.group(1)): normalize(match.group(2))
        for match in re.finditer(r"(?m)^([A-Za-z][A-Za-z ]+):\s*(.+?)\s*$", preamble)
    }


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
    return normalize(value).lower() in EMPTY_VALUES or normalize(value).startswith("<")


def contains_all(value: str, *terms: str) -> bool:
    lowered = value.lower()
    return all(term.lower() in lowered for term in terms)


def dialect_warnings(text: str, fields: dict[str, str], sections: dict[str, str]) -> list[str]:
    """Return additive v2 guidance; never invalidate a legacy v1 spine by default."""
    warnings: list[str] = []
    dod = sections.get("Definition Of Done", "")
    if not (re.search(r"(?im)^\s*SHIP\b", dod) and re.search(r"(?im)^\s*HARDEN\b", dod)):
        warnings.append("v2 Definition Of Done should have SHIP and HARDEN tiers; flat v1 checklists remain supported")
    else:
        ship = re.split(r"(?im)^\s*HARDEN\b", dod, maxsplit=1)[0]
        steps = re.findall(r"(?m)^\s*-\s*\[[ xX]\]\s*(\d+)\.", ship)
        if not 5 <= len(steps) <= 12:
            warnings.append("v2 SHIP journey should contain 5-12 numbered checkbox steps")
        for label, terms in (
            ("real browser and live deployment", ("real browser", "live")),
            ("first-breakage fix/deploy/restart loop", ("first breakage", "deploy", "step 1")),
            ("per-step screenshots", ("screenshot", "step")),
            ("test-package handoff", ("manually walked", "now you test")),
        ):
            if not contains_all(ship, *terms):
                warnings.append(f"v2 SHIP journey should state the {label} contract")
        for number, line in re.findall(r"(?m)^\s*-\s*\[[ xX]\]\s*(\d+)\.\s*(.+)$", ship):
            if "test package" not in line.lower() and not re.search(r"\b(PORT|DUPLICATE|BUILD)\b", line, re.I):
                warnings.append(f"v2 SHIP step {number} lacks PORT/DUPLICATE/BUILD marking")

    roles = sections.get("Role Bindings", "")
    if not contains_all(roles, "Epic worker", "MANAGER", "dispatch", "walk"):
        warnings.append("v2 Epic-worker role should contain the manager mandate")
    if not (contains_all(roles, "Ticket worker", "FIRST ACTION", "git worktree add") and re.search(r"never .*?(checkout|switch)|never (checkout|switch)", roles, re.I | re.S)):
        warnings.append("v2 Ticket-worker role should require worktree first action and ban shared-clone checkout/switch")
    if not ("Ticket worker" in roles and re.search(r"PORT/DUPLICATE.*fail|scratch.*duplicat.*fail", roles, re.I | re.S)):
        warnings.append("v2 Ticket-worker role should make scratch duplication fail review")

    current = sections.get("Current State", "")
    if not contains_all(current, "base", "pinned", "no rebase"):
        warnings.append("v2 Current State should record a pinned base and no-rebases-until-journey-passes rule")
    status = fields.get("Status", "")
    gated = "dispatch only after" in status.lower() or "pending" in status.lower() and "gate" in status.lower()
    if gated and not ("dispatch" in current.lower() and ("gate" in current.lower() or "condition" in current.lower())):
        warnings.append("gated status should repeat its dispatch condition in Current State")
    if "superseded" in status.lower() and not contains_all(status, "by", "do not execute"):
        warnings.append("SUPERSEDED status should name the replacement and say do not execute")

    decisions = sections.get("Decisions", "")
    if not contains_all(decisions, "anything unanswered", "simplest option", "journal", "keep moving"):
        warnings.append("v2 Decisions should include the simplest-option/journal/keep-moving catch-all")

    ledger = sections.get("Issue Ledger", "")
    header, rows = parse_table(ledger)
    for concept, alternatives in (
        ("Wave", ("Wave",)), ("Budget", ("Budget",)),
        ("worktree dispatch record", ("Worktree", "Worktree / PR / Branch")),
        ("PORT/DUPLICATE/BUILD method", ("Method", "Source", "Origin")),
    ):
        if not any(name in header for name in alternatives):
            warnings.append(f"v2 Issue Ledger should include {concept}")
    if rows and header:
        pos = {name: i for i, name in enumerate(header)}
        method_col = next((name for name in ("Method", "Source", "Origin") if name in pos), None)
        title_col = "Title" if "Title" in pos else None
        for n, row in enumerate(rows, 1):
            haystack = " ".join(row[pos[name]] for name in (title_col, method_col) if name)
            if not re.search(r"\b(PORT|DUPLICATE|BUILD)\b", haystack, re.I):
                warnings.append(f"v2 ledger row {n} lacks PORT/DUPLICATE/BUILD marking")
            for column in ("Wave", "Budget", "Worktree"):
                if column in pos and is_empty(row[pos[column]]):
                    warnings.append(f"v2 ledger row {n} has no {column}")
        first = " ".join(rows[0][pos[name]] for name in ("Title", "Acceptance") if name in pos)
        if not re.search(r"touchable|deploy|running|open|URL|login|script|demo|journey step", first, re.I):
            warnings.append("v2 first ledger ticket should be the earliest human-touchable milestone")

    gates = sections.get("Human Gates", "")
    gate_header, gate_rows = parse_table(gates)
    for required in ("Gate", "Human Owner", "Trigger", "Exact Approval / Input Required"):
        if required not in gate_header:
            warnings.append(f"v2 Human Gates should include column: {required}")
    if not ("BLOCKED ON" in gates and re.search(r"entire (next )?(message|status)", gates, re.I)):
        warnings.append("v2 Human Gates should state the entire-message BLOCKED ON protocol")

    recovery = sections.get("Recovery And Takeover", "")
    if not contains_all(recovery, "manager reassigns", "silent past", "budget"):
        warnings.append("v2 Recovery should reassign tickets silent past budget")
    if "none permitted" not in sections.get("Open Questions", "").lower():
        warnings.append("v2 Open Questions healthy state is: None permitted")

    whole = text.lower()
    if not ("30 min" in whole and "lap/state | blocker | eta" in whole and "two consecutive eta" in whole):
        warnings.append("v2 spine should define the 30-minute heartbeat and two-ETA-slip rule")
    if not re.search(r"live customer data.*snapshot.*checksum.*restore drill", whole, re.S):
        warnings.append("v2 spine should define proportional ceremony by risk class")
    if not re.search(r"wave 1.*wave 2.*(journey|then)", whole, re.S):
        warnings.append("v2 spine should define disjoint waves followed by the manager journey loop")
    appendix = sections.get("Appendix", "")
    if not ("input" in appendix.lower() and ("absence rule" in appendix.lower() or "non-blocking" in appendix.lower())):
        warnings.append("v2 Appendix should list human inputs with absence-rules")
    if "worker dispatch prompt" not in appendix.lower():
        warnings.append("v2 Appendix should store versioned Worker Dispatch Prompts")
    if "no human in the loop" in whole:
        warnings.append("banned v2 phrase: no human in the loop")
    return warnings


def validate(path: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    fields = parse_fields(text)
    sections = parse_sections(text)

    for field in REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"missing field: {field}")
        elif is_empty(fields[field]):
            warnings.append(f"unresolved field: {field}")

    for section in REQUIRED_SECTIONS:
        if section not in sections:
            errors.append(f"missing section: {section}")

    ledger = sections.get("Issue Ledger", "")
    header, rows = parse_table(ledger)
    if not header:
        errors.append("Issue Ledger has no Markdown table")
    else:
        for column in REQUIRED_LEDGER_COLUMNS:
            if column not in header:
                errors.append(f"Issue Ledger missing column: {column}")

        positions = {name: index for index, name in enumerate(header)}
        if all(name in positions for name in ("Issue", "Owner / Assignment", "Status", "PR/Branch", "Base", "Latest Evidence", "Last Verified", "Next Action")):
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

    warnings.extend(dialect_warnings(text, fields, sections))

    return {"path": str(path), "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable results")
    args = parser.parse_args()

    results = []
    exit_code = 0
    for path in args.paths:
        if not path.is_file():
            result = {"path": str(path), "errors": ["file not found"], "warnings": []}
        else:
            result = validate(path)
        results.append(result)
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
