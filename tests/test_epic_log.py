"""Epic log: spine_new scaffold, spines.py discovery, and the pre-commit tree gate (hermetic temp repos)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_agents_block import agents_block
from test_validate_spine import VALIDATOR_PATH, validate_spine as v

SCRIPTS = VALIDATOR_PATH.parent
sys.path.insert(0, str(SCRIPTS))
import spines  # noqa: E402

ROOT = """# EPIC: Root

Spine profile: compact
Ticket backend: github
Spine dialect: v1
Repository: a/b
Primary document: docs/root.md
Spine ID: root
Spine Type: root
Root spine: self
Parent spine: none
Additional root rationale: n/a
Integration branch: main

## Current State

Owner: me
Status: active
Last attempted: x
Result: y
Evidence: z
Waiting on: none
Approved work: none
Next action: go
Source revision: abc
Verified at: 2026-10-19

## Mission

Purpose.

## Non-Goals

None.

## Definition Of Done

- [ ] R-1 purpose met

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| draft | Ticket worker | me | t | draft | none | none | none | none | 2026-10-19 | n |

## Decisions

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-10-19 | accepted | c | r | e | n |
"""
E4 = "# E4 one logger\n\nStatus: PAUSED\n\n## Tickets\n\n| # | Ticket | State |\n|---|---|---|\n| 1 | stream registry | open |\n"  # a page: no EPIC-<n> title, no Spine ID
STAMPED = E4.replace("# E4 one logger", "# EPIC-9: one logger")  # an epic by its stamp, still without the v1 header
COMPLIANT = "# EPIC-9: one logger\n\n## Goal\n\nG.\n\n## Serves\n\nThe repo.\n\n## Done means\n\n- [ ] X-1 y\n\n## Current State\n\nStatus: draft\n"  # passes the new-epic doctrine check
MAP_HEAD = "## Spine Map\n\n| Spine ID | Relationship | Spine | Purpose | Status | Health / Blocker | Latest Evidence | Last Rolled Up | Next Action |\n|---|---|---|---|---|---|---|---|---|\n"


class EpicLogCase(unittest.TestCase):
    root_text = ROOT

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-log-")
        self.repo = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.repo / "docs").mkdir()
        (self.repo / "AGENTS.md").write_text("Root spine: docs/root.md. Read its Current State.\n")
        self.write("docs/root.md", self.root_text)

    def write(self, name: str, text: str) -> Path:
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), "--repo", str(self.repo), *args], capture_output=True, text=True)

    def new(self, path: str = "docs/E4-one-logger.md", parent: str = "docs/root.md", title: str = "E4 one logger", *more: str) -> subprocess.CompletedProcess:
        return self.run_script("spine_new.py", "--parent", parent, "--path", path, "--title", title, *more)

    def log(self) -> dict:
        return json.loads(self.run_script("spines.py", "--json").stdout)


class SpineNewTests(EpicLogCase):
    def test_creates_valid_registered_spine(self) -> None:
        done = self.new()
        self.assertEqual(0, done.returncode, done.stderr)
        child = self.repo / "docs/E4-one-logger.md"
        self.assertTrue(v.trackable(child)["trackable"], v.trackable(child))
        self.assertEqual([], v.validate_local(child).errors)
        text = child.read_text()
        for line in ("Spine ID: e4-one-logger", "Root spine: [Root](root.md)", "Parent spine: [Root](root.md)", "Status: ready", "# EPIC-1: E4 one logger", "## Goal", "## Serves", "## Done means", "- [ ] E1-1 "):
            self.assertIn(line, text)
        self.assertNotIn("Spine Type", text)
        root = self.repo / "docs/root.md"
        self.assertIn("| e4-one-logger | child | [EPIC-1: E4 one logger](E4-one-logger.md) |", root.read_text())
        self.assertEqual([], v.validate_local(root).errors)

    def test_idempotent_and_never_overwrites(self) -> None:
        self.new()
        root = self.repo / "docs/root.md"
        child = self.repo / "docs/E4-one-logger.md"
        before = (root.read_text(), child.read_text())
        again = self.new()
        self.assertEqual(0, again.returncode)
        self.assertIn("already in", again.stdout)
        self.assertEqual(before, (root.read_text(), child.read_text()))
        self.assertEqual(1, root.read_text().count("e4-one-logger"))
        plain = self.write("docs/E9-plain.md", E4)  # a file with no header: not a spine, never overwritten
        refused = self.new("docs/E9-plain.md", title="E9")
        self.assertEqual(1, refused.returncode)
        self.assertIn("refusing to overwrite", refused.stderr)
        self.assertEqual(E4, plain.read_text())

    def test_exists_but_unregistered_gets_registered(self) -> None:
        self.new()
        root = self.repo / "docs/root.md"
        root.write_text(self.root_text)  # forget the registration
        self.assertEqual(0, self.new().returncode)
        self.assertIn("e4-one-logger", root.read_text())

    def test_parent_by_spine_id_nested_and_existing_map(self) -> None:
        self.write("docs/root.md", self.root_text + "\n" + MAP_HEAD)
        self.assertEqual(0, self.new("docs/E4-one-logger.md", "docs/root.md", "E4 one logger", "--purpose", "One logger").returncode)
        nested = self.new("docs/e4/E4-1-streams.md", "e4-one-logger", "E4-1 streams", "--purpose", "One registry")
        self.assertEqual(0, nested.returncode, nested.stderr)
        child = self.repo / "docs/e4/E4-1-streams.md"
        self.assertIn("Parent spine: [EPIC-1: E4 one logger](../E4-one-logger.md)", child.read_text())
        self.assertIn("Root spine: [Root](../root.md)", child.read_text())
        self.assertIn("| e4-1-streams | child | [EPIC-2: E4-1 streams](e4/E4-1-streams.md) | One registry |", (self.repo / "docs/E4-one-logger.md").read_text())
        self.assertEqual(1, (self.repo / "docs/root.md").read_text().count("## Spine Map"))
        graph = [str(self.repo / n) for n in ("docs/root.md", "docs/E4-one-logger.md", "docs/e4/E4-1-streams.md")]
        checked = subprocess.run([sys.executable, "-B", str(VALIDATOR_PATH), "--strict", "--graph", *graph], capture_output=True, text=True)
        self.assertEqual(0, checked.returncode, checked.stdout)

    def test_refuses_without_root_or_parent_header(self) -> None:
        self.assertEqual(1, self.new(parent="nope").returncode)
        self.write("docs/loose.md", "# loose\n")
        self.assertIn("no Spine ID", self.new(parent="docs/loose.md").stderr)
        self.write("AGENTS.md", "Root spine: none. Read nothing.\n")
        self.assertIn("no root spine", self.new().stderr)


class DiscoveryTests(EpicLogCase):
    def test_tree_rollup_and_dod_leaves(self) -> None:
        self.new()
        self.new("docs/e4/E4-1-streams.md", "e4-one-logger", "E4-1 streams")
        child = self.repo / "docs/e4/E4-1-streams.md"
        child.write_text(child.read_text().replace("Status: ready", "Status: done").replace("- [ ] E2-", "- [x] E2-"))
        log = self.log()
        self.assertEqual("docs/root.md", log["root"])
        by = {n["path"]: n for n in log["nodes"]}
        self.assertEqual(["docs/E4-one-logger.md"], by["docs/root.md"]["children"])
        self.assertEqual("docs/root.md", by["docs/E4-one-logger.md"]["parent"])
        self.assertEqual({"id": "R-1", "text": "purpose met", "done": False}, by["docs/root.md"]["dod"][0])
        self.assertEqual(["docs/e4/E4-1-streams.md"], by["docs/E4-one-logger.md"]["children"])
        leaf = by["docs/e4/E4-1-streams.md"]
        self.assertEqual(("done", "done", True), (leaf["status"], leaf["rollup_status"], leaf["dod"][0]["done"]))
        self.assertEqual("ready", by["docs/E4-one-logger.md"]["status"])
        self.assertEqual("active", by["docs/E4-one-logger.md"]["rollup_status"])  # a done child, an open criterion
        self.assertEqual(([], []), (log["orphans"], log["mismatches"]))
        text = self.run_script("spines.py").stdout
        self.assertIn("- Root (docs/root.md) active", text)
        self.assertIn("  [ ] R-1 purpose met", text)
        self.assertIn("    - EPIC-2: E4-1 streams (docs/e4/E4-1-streams.md) done", text)

    def test_rollup_rules(self) -> None:
        dod = lambda *done: [{"done": d} for d in done]  # noqa: E731
        self.assertEqual("done", spines.rollup("active", ["done"], dod(True)))
        self.assertEqual("blocked", spines.rollup("active", ["blocked", "done"], []))
        self.assertEqual("active", spines.rollup("draft", ["done", "ready"], []))
        self.assertEqual("ready", spines.rollup("ready", ["ready"], dod(False)))
        self.assertEqual("draft", spines.rollup("", [], []))

    def test_orphans_skip_rules_and_linked_children(self) -> None:
        self.write("docs/E4-ONE-LOGGER.md", STAMPED)
        self.write("docs/loose.md", "# Loose\n\nSpine ID: loose\n")
        self.write("docs/plans/PLAN-x.md", "# Plan\n")
        self.write("docs/notes.md", "# notes about explanation\n")
        self.write("docs/archive/E1-old.md", STAMPED)
        self.write("node_modules/p/EPIC-x.md", STAMPED)
        self.write(".claude/skills/epic-spine/SKILL.md", "---\nname: epic-spine\n---\n")
        self.write(".claude/skills/epic-spine/assets/t.md", "Spine ID: <id>\n")
        self.write("vendor/epic-spine/SKILL.md", "x")
        self.write("vendor/epic-spine/assets/t.md", "Spine ID: <id>\n")
        self.write("docs/handoffs/2026-spine-gap.md", "# handoff\n")
        self.write("docs/E7-linked.md", "# linked\n")
        self.write("console/server/test/real/SPINE-fixture.md", "# fixture\n")
        self.write("tests/E1-fixture.md", STAMPED)
        self.write("docs/loose.md", "# Loose\n\nSpine ID: loose\n\n## Spine Map\n\n" + MAP_HEAD.split("\n\n", 1)[1] + "| e7 | child | [E7](E7-linked.md) | p | draft | none | none | d | n |\n")
        orphans = {o["path"]: o["reason"] for o in self.log()["orphans"]}
        # an epic is a Spine ID or an EPIC-<n> title, never a name: PLAN-x.md and notes.md are pages (test_doctrine.py)
        self.assertEqual({"docs/E4-ONE-LOGGER.md": "no Spine ID header", "docs/loose.md": "not reachable from the root", "docs/E7-linked.md": "no Spine ID header"}, orphans)

    def test_repo_relative_links_resolve_like_agent_team(self) -> None:
        self.new()
        row = "| e4-one-logger | child | [E4 one logger](docs/spines/m2.md) |"
        root = (self.repo / "docs/root.md").read_text().replace("| e4-one-logger | child | [EPIC-1: E4 one logger](E4-one-logger.md) |", row)
        child = (self.repo / "docs/E4-one-logger.md").read_text().replace("Parent spine: [Root](root.md)", "Parent spine: docs/spines/root.md")
        (self.repo / "docs/root.md").unlink()
        (self.repo / "docs/E4-one-logger.md").unlink()
        self.write("AGENTS.md", "Root spine: docs/spines/root.md. Read its Current State.\n")
        self.write("docs/spines/root.md", root)
        self.write("docs/spines/m2.md", child)
        log = self.log()
        self.assertEqual(("docs/spines/root.md", [], []), (log["root"], log["orphans"], log["mismatches"]))
        by = {n["path"]: n for n in log["nodes"]}
        self.assertEqual(["docs/spines/m2.md"], by["docs/spines/root.md"]["children"])
        self.assertEqual("docs/spines/root.md", by["docs/spines/m2.md"]["parent"])

    def test_mismatches(self) -> None:
        self.new()
        self.new("docs/E5-b.md", title="E5 b")
        root = self.repo / "docs/root.md"
        # E5 says its parent is E4, but only the root's map lists it; E4 is listed by the root and names it.
        e5 = self.repo / "docs/E5-b.md"
        e5.write_text(e5.read_text().replace("Parent spine: [Root](root.md)", "Parent spine: [E4](E4-one-logger.md)"))
        # a header-only child: not in any map
        self.write("docs/E6-c.md", e5.read_text().replace("e5-b", "e6-c").replace("E5 b", "E6 c").replace("Parent spine: [E4](E4-one-logger.md)", "Parent spine: [Root](root.md)"))
        root.write_text(root.read_text() + "| gone | child | [Gone](gone.md) | p | draft | none | none | d | n |\n")
        problems = {(m["path"], m["problem"]) for m in self.log()["mismatches"]}
        self.assertIn(("docs/E5-b.md", "listed in this Spine Map but its Parent spine is docs/E4-one-logger.md"), problems)
        self.assertIn(("docs/E5-b.md", "not in the parent's Spine Map"), problems)
        self.assertIn(("docs/E6-c.md", "not in the parent's Spine Map"), problems)
        self.assertIn(("docs/root.md", "Spine Map row points at a missing file"), problems)
        by = {n["path"]: n for n in self.log()["nodes"]}
        self.assertIn("docs/E5-b.md", by["docs/E4-one-logger.md"]["children"])  # the child's header decides
        self.assertIn("docs/E6-c.md", by["docs/root.md"]["children"])

    def test_no_root_everything_is_an_orphan(self) -> None:
        self.write("AGENTS.md", "Root spine: none. Read nothing.\n")
        self.write("docs/E4-ONE-LOGGER.md", STAMPED)
        done = self.run_script("spines.py", "--json")
        self.assertEqual(0, done.returncode)
        log = json.loads(done.stdout)
        self.assertEqual((None, []), (log["root"], log["nodes"]))
        self.assertEqual({"docs/E4-ONE-LOGGER.md", "docs/root.md"}, {o["path"] for o in log["orphans"]})
        self.assertEqual(([], []), (log["orphan_pages"], log["looks_like_epic"]))
        self.assertIn("no root spine", self.run_script("spines.py").stdout)

    def test_root_found_from_header_without_agents(self) -> None:
        (self.repo / "AGENTS.md").unlink()
        self.assertEqual("docs/root.md", self.log()["root"])


class PreCommitTreeTests(EpicLogCase):
    def setUp(self) -> None:
        super().setUp()
        self.git("init", "-q")
        agents_block.install(self.repo, "docs/root.md")
        self.git("add", "-A")
        self.assertEqual(0, self.git("commit", "--no-verify", "-m", "base").returncode)  # history before the hook: an old-style root

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.repo, capture_output=True, text=True)

    def commit(self, name: str, text: str | None = None) -> subprocess.CompletedProcess:
        if text is not None:
            self.write(name, text)
        self.git("add", "-A")
        return self.git("commit", "-m", "x")

    def test_unregistered_goal_doc_is_blocked_until_scaffolded(self) -> None:
        blocked = self.commit("docs/E4-ONE-LOGGER.md", STAMPED)
        self.assertNotEqual(0, blocked.returncode)
        self.assertIn("docs/E4-ONE-LOGGER.md: not in the epic log: E4-ONE-LOGGER.md: no Spine ID header", blocked.stderr)
        self.assertIn("spine_new.py --repo . --parent <parent spine> --path docs/E4-ONE-LOGGER.md", blocked.stderr)
        self.git("reset", "-q")
        (self.repo / "docs/E4-ONE-LOGGER.md").unlink()
        self.assertEqual(0, self.new("docs/E4-ONE-LOGGER.md").returncode)
        ok = self.commit("docs/E4-ONE-LOGGER.md")
        self.assertEqual(0, ok.returncode, ok.stderr)

    def test_header_without_registration_or_parent_is_blocked(self) -> None:
        self.new()
        self.git("add", "-A")
        self.assertEqual(0, self.git("commit", "-m", "ok").returncode)
        root = self.repo / "docs/root.md"
        root.write_text(self.root_text)  # the parent forgets the child
        blocked = self.commit("docs/E4-one-logger.md", (self.repo / "docs/E4-one-logger.md").read_text() + "\nedit\n")
        self.assertNotEqual(0, blocked.returncode)
        self.assertIn("not in the parent's Spine Map", blocked.stderr)
        self.git("reset", "-q")
        self.write("docs/E8-loose.md", (self.repo / "docs/E4-one-logger.md").read_text().replace("Parent spine: [Root](root.md)", "Parent spine: none"))
        self.assertIn("Parent spine missing or not a file", self.commit("docs/E8-loose.md").stderr)

    def legacy_head(self, name: str = "docs/E4-ONE-LOGGER.md") -> None:
        self.write(name, STAMPED)
        self.git("add", "-A")
        self.assertEqual(0, self.git("commit", "--no-verify", "-m", "legacy").returncode)

    def test_modified_legacy_goal_doc_warns_and_passes(self) -> None:
        self.legacy_head()
        done = self.commit("docs/E4-ONE-LOGGER.md", STAMPED + "\nmore\n")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("docs/E4-ONE-LOGGER.md: not in the epic log", done.stderr)
        self.assertIn("legacy goal doc, not blocked", done.stderr)
        self.assertIn("spine_new.py", done.stderr)

    def test_renamed_legacy_goal_doc_is_blocked(self) -> None:
        self.legacy_head()
        self.git("mv", "docs/E4-ONE-LOGGER.md", "docs/E5-ONE-LOGGER.md")
        blocked = self.git("commit", "-m", "mv")
        self.assertNotEqual(0, blocked.returncode)
        self.assertIn("docs/E5-ONE-LOGGER.md: not in the epic log", blocked.stderr)

    def test_root_without_spine_id_warns_and_passes(self) -> None:
        self.write("docs/EPIC.md", "# EPIC\n\n## Current State\n\nOwner: me\n")
        self.write("AGENTS.md", (self.repo / "AGENTS.md").read_text().replace("Root spine: docs/root.md.", "Root spine: docs/EPIC.md."))
        self.git("add", "-A")
        self.assertEqual(0, self.git("commit", "--no-verify", "-m", "legacy root").returncode)
        done = self.commit("docs/E4-ONE-LOGGER.md", COMPLIANT)
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("root spine has no Spine ID header: migrate the root first", done.stderr)
        self.assertEqual(1, done.stderr.count("migrate the root first"))

    def test_non_goal_docs_pass(self) -> None:
        self.assertEqual(0, self.commit("docs/notes.md", "# notes\n").returncode)
        self.assertEqual(0, self.commit("docs/explanation-planning.md", "# notes\n").returncode)

    def test_no_root_spine_only_warns(self) -> None:
        self.write("AGENTS.md", (self.repo / "AGENTS.md").read_text().replace("Root spine: docs/root.md.", "Root spine: none."))
        self.assertEqual(0, self.commit("AGENTS.md").returncode)
        warned = self.commit("docs/E4-ONE-LOGGER.md", COMPLIANT)
        self.assertEqual(0, warned.returncode, warned.stderr)
        self.assertIn("no root spine: goal docs are not checked", warned.stderr)


if __name__ == "__main__":
    unittest.main()
