"""Persona files, epic Team tables and the assignee rule (references/personas.md); legacy spines (no Team section) stay untouched."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"))
import spines  # noqa: E402
import validate_spine as v  # noqa: E402

PERSONA = "---\nname: {n}\ntemplate: worker\nmodel: sonnet\nhost: vps1\n{x}---\n\n## Remit\n\nr\n\n## Reads\n\nr\n\n## Writes\n\nw\n"
ROW = "| https://github.com/o/r/issues/{n} | Worker | {who} | t | {st} | none | b | main | e | 2026-10-24 | go |\n"
LEDGER = "| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
TEAM = "## Team\n\n| Persona | Cadence | Write scope | Notes |\n|---|---|---|---|\n| Watcher | daily | this spine | n |\n| Fixer | hourly | repo | n |\n\n"


def epic(rows: list[tuple[str, str]], team: str = TEAM) -> str:
    body = "".join(ROW.format(n=i + 1, who=who, st=st) for i, (who, st) in enumerate(rows))
    return f"""# EPIC-1: T

Spine profile: compact
Repository: o/r
Primary document: docs/EPIC-1-T.md
Spine ID: t
Integration branch: main

## Mission

m

{team}## Current State

Owner: o
Status: active
Last attempted: x
Result: x
Evidence: x
Waiting on: none
Approved work: none
Next action: x
Source revision: main
Verified at: 2026-10-24

## Non-Goals

n

## Definition Of Done

- [ ] D-1 d

## Issue Ledger

{LEDGER}{body}
## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-24 | accepted | d | d | e | never |
"""


class PersonaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / ".git").mkdir()
        (self.repo / "docs").mkdir()
        (self.repo / "personas").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def persona(self, name: str, extra: str = "", text: str | None = None) -> list[str]:
        path = self.repo / "personas" / f"{name}.md"
        path.write_text(text or PERSONA.format(n=name, x=extra))
        return v.validate_local(path).errors

    def check(self, text: str, files: tuple[str, ...] = ()) -> list[str]:
        for f in files:
            self.persona(f)
        path = self.repo / "docs" / "EPIC-1-T.md"
        path.write_text(text)
        return v.validate_local(path).errors

    def test_valid_persona_file(self):
        self.assertEqual(self.persona("watcher"), [])

    def test_missing_frontmatter_key(self):
        self.assertEqual(self.persona("watcher", text=PERSONA.format(n="watcher", x="").replace("host: vps1\n", "")), ["persona file missing frontmatter key: host"])

    def test_missing_body_section(self):
        self.assertEqual(self.persona("watcher", text=PERSONA.format(n="watcher", x="").replace("## Writes", "## Other")), ["persona file missing section: ## Writes"])

    def test_forbidden_fields_and_sections(self):
        for key in ("goal: g\n", "cadence: daily\n", "write_scope: x\n", "Write-Scope: x\n"):
            self.assertTrue(any("belongs to the assignment" in e for e in self.persona("watcher", key)), key)
        errors = self.persona("watcher", text=PERSONA.format(n="watcher", x="") + "\n## Cadence\n\nhourly\n")
        self.assertTrue(any("## Cadence" in e for e in errors))

    def test_name_must_match_file(self):
        self.assertTrue(any("does not match" in e for e in self.persona("watcher", text=PERSONA.format(n="fixer", x=""))))

    def test_valid_team_and_assignees(self):
        self.assertEqual(self.check(epic([("Watcher", "active"), ("Jordi", "blocked"), ("Fixer", "done"), ("none", "draft")])), [])

    def test_team_table_shape(self):
        self.assertIn("Team table missing column: Write scope", self.check(epic([], "## Team\n\n| Persona | Cadence | Notes |\n|---|---|---|\n| Watcher | daily | n |\n\n")))
        self.assertIn("Team row 1 (watcher) has empty Cadence", self.check(epic([], "## Team\n\n| Persona | Cadence | Write scope | Notes |\n|---|---|---|---|\n| Watcher |  | x | n |\n\n")))
        self.assertIn("Team lists watcher twice", self.check(epic([], TEAM + "").replace("| Fixer |", "| Watcher |")))

    def test_extra_team_columns_allowed(self):
        team = "## Team\n\n| Persona | Cadence | Reads | Write scope | Notes |\n|---|---|---|---|---|\n| Watcher | daily | x | y | n |\n\n"
        self.assertEqual(self.check(epic([("Watcher", "ready")], team)), [])

    def test_team_header_parenthetical_ignored(self):
        team = "## Team\n\n| Persona | Cadence (console) | Write scope (only these) | Notes |\n|---|---|---|---|\n| Watcher | daily | this spine | n |\n\n"
        self.assertEqual(self.check(epic([("Watcher", "ready")], team)), [])
        self.assertIn("Team row 1 (watcher) has empty Cadence", self.check(epic([], team.replace("| daily |", "|  |"))))
        self.assertIn("Team table missing column: Write scope", self.check(epic([], team.replace("Write scope (only these)", "Scope (only these)"))))
        self.assertEqual(spines.P.team_json(v.table_rows(team))[0]["write_scope"], "this spine")

    def test_unknown_assignee_rejected(self):
        errors = self.check(epic([("Watcher", "ready"), ("Stranger", "ready"), ("unassigned", "done")]))
        self.assertEqual(len(errors), 2)
        self.assertTrue(all("not a team persona or Jordi" in e for e in errors))

    def test_draft_row_may_be_unassigned(self):
        self.assertEqual(self.check(epic([("unassigned", "draft")])), [])

    def test_persona_files_define_the_team(self):
        self.assertEqual(self.check(epic([("Watcher", "ready")]), files=("watcher", "fixer")), [])
        (self.repo / "personas" / "fixer.md").unlink()
        self.assertIn("Team persona fixer has no file personas/fixer.md", self.check(epic([("Watcher", "ready")]), files=("watcher",)))
        self.assertTrue(any("'Fixer'" not in e and "Stranger" in e for e in self.check(epic([("Stranger", "ready")]), files=("watcher", "fixer"))))

    def test_legacy_spine_untouched(self):
        legacy = epic([("unassigned", "ready"), ("worker (run_1)", "active"), ("/root/delivery", "done")], team="")
        self.assertNotIn("## Team", legacy)
        self.assertEqual(self.check(legacy), [])

    def test_listing_personas_teams_and_queues(self):
        self.persona("watcher")
        self.persona("fixer")
        (self.repo / "AGENTS.md").write_text("Root spine: docs/EPIC-1-T.md\n")
        (self.repo / "docs/EPIC-1-T.md").write_text(epic([("Watcher", "ready"), ("Watcher", "done"), ("Fixer", "active"), ("Jordi", "blocked"), ("Watcher", "draft")]).replace("Spine ID: t\n", "Spine ID: t\nSpine Type: root\nRoot spine: self\nParent spine: none\n"))
        log = spines.scan(self.repo)
        self.assertEqual([t["persona"] for t in log["nodes"][0]["team"]], ["watcher", "fixer"])
        by = {p["name"]: p for p in log["personas"]}
        self.assertEqual(by["watcher"]["template"], "worker")
        self.assertEqual(by["watcher"]["epics"], ["docs/EPIC-1-T.md"])
        self.assertEqual([r["issue"] for r in by["watcher"]["queue"]], ["https://github.com/o/r/issues/1"])
        self.assertEqual([r["issue"] for r in by["fixer"]["queue"]], ["https://github.com/o/r/issues/3"])
        self.assertEqual([r["issue"] for r in by["Jordi"]["queue"]], ["https://github.com/o/r/issues/4"])

    def test_cli_checks_persona_files(self):
        self.persona("watcher")
        self.assertEqual(v.validate_local(self.repo / "personas" / "watcher.md").errors, [])


if __name__ == "__main__":
    unittest.main()
