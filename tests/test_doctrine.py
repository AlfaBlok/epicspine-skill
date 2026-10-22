"""Doctrine 2 tools (EPIC-4 step 3): spines.py --json doctrine fields, epic detection, spine_new scaffold, pre_commit block/advisories."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest

import test_epic_log as base
import tree_gate
from test_validate_spine import VALIDATOR_PATH, validate_spine as v

SCRIPTS = VALIDATOR_PATH.parent
sys.path.insert(0, str(SCRIPTS))
import doctrine  # noqa: E402

PAGE_GOAL = "# Plan page\n\n## Goal\n\nWhat we want.\n\n## Done means\n\n- [ ] X-1 it works\n"


class FieldTests(base.EpicLogCase):
    def child(self, **kw) -> dict:
        self.assertEqual(0, self.new("docs/EPIC-one.md", "docs/root.md", "one", "--purpose", "Why one exists", *kw.get("more", ())).returncode)
        return {n["path"]: n for n in self.log()["nodes"]}

    def test_scaffold_fields(self) -> None:
        node = self.child()["docs/EPIC-one.md"]
        self.assertEqual("Why one exists", node["goal"])
        self.assertTrue(node["serves"].startswith("[EPIC-0: Root](root.md)"), node["serves"])
        self.assertEqual([{"id": "E1-1", "text": "<observable outcome and how it is measured>", "done": False},
                          {"id": "E1-2", "text": "<a second outcome (2-5 in all), or delete this line>", "done": False}], node["done_means"])
        self.assertEqual(node["done_means"], node["dod"])  # rollup reads the new heading too
        self.assertEqual([], node["missing_sections"])
        self.assertEqual(("ready", {"long_cells": 0}), (node["status"], {"long_cells": node["size"]["long_cells"]}))
        self.assertEqual(len((self.repo / "docs/EPIC-one.md").read_text().splitlines()), node["size"]["lines"])
        self.assertEqual([], node["pages"])
        self.assertEqual({}, node["contributes"])

    def test_contributes_keyed_by_child_path_and_placeholder_is_absent(self) -> None:
        by = self.child()
        self.assertEqual({"docs/EPIC-one.md": "Why one exists"}, by["docs/root.md"]["contributes"])
        self.assertEqual(0, self.new("docs/EPIC-two.md", "docs/root.md", "two").returncode)  # no --purpose: placeholder sentence
        root = {n["path"]: n for n in self.log()["nodes"]}["docs/root.md"]
        self.assertEqual({"docs/EPIC-one.md": "Why one exists"}, root["contributes"])
        self.assertIn("docs/EPIC-two.md", root["children"])

    def test_root_missing_sections_and_serves_null(self) -> None:
        root = self.child()["docs/root.md"]
        self.assertEqual((None, []), (root["serves"], root["missing_sections"]))  # the root needs no Serves
        self.assertEqual("Purpose.", root["goal"])  # Mission counts as Goal
        self.assertEqual([{"id": "R-1", "text": "purpose met", "done": False}], root["done_means"])  # DoD heading is the fallback

    def test_missing_sections_names(self) -> None:
        self.child()
        self.write("docs/EPIC-bare.md", "# EPIC-9: bare\n\nSpine ID: bare\nRoot spine: [EPIC-0: Root](root.md)\nParent spine: [EPIC-0: Root](root.md)\n\n## Notes\n\nx\n")
        node = {n["path"]: n for n in self.log()["nodes"]}["docs/EPIC-bare.md"]
        self.assertEqual(["goal", "serves", "done_means", "status"], node["missing_sections"])
        self.assertEqual((None, None, []), (node["goal"], node["serves"], node["done_means"]))
        self.write("docs/EPIC-bare.md", "# bare\n\nSpine ID: bare\nRoot spine: [EPIC-0: Root](root.md)\nParent spine: [EPIC-0: Root](root.md)\n")
        self.assertEqual(["title", "goal", "serves", "done_means", "status"], {n["path"]: n for n in self.log()["nodes"]}["docs/EPIC-bare.md"]["missing_sections"])

    def test_done_means_prefers_its_heading_and_empty_goal_is_missing(self) -> None:
        text = "# EPIC-3: t\n\n## Goal\n<!-- only a comment -->\n\n## Done means\n\n- [x] A-1 done thing\n\n## Definition Of Done\n\n- [ ] B-1 old\n\n## Current State\n\nStatus: active\n"
        found = doctrine.fields(text)
        self.assertEqual([{"id": "A-1", "text": "done thing", "done": True}], found["done_means"])
        self.assertEqual((None, ["goal", "serves"]), (found["goal"], found["missing_sections"]))
        self.assertEqual([], doctrine.fields(text.replace("<!-- only a comment -->", "Real."), root=True)["missing_sections"])

    def test_size_counts_long_cells(self) -> None:
        self.child()
        path = self.repo / "docs/EPIC-one.md"
        path.write_text(path.read_text() + f"\n| a | {'x' * 201} |\n| {'y' * 200} | b |\n")
        self.assertEqual(1, {n["path"]: n for n in self.log()["nodes"]}["docs/EPIC-one.md"]["size"]["long_cells"])


class PageTests(base.EpicLogCase):
    def test_pages_follow_links_through_pages_with_via(self) -> None:
        self.assertEqual(0, self.new("docs/EPIC-one.md", "docs/root.md", "one").returncode)
        self.write("docs/EPIC-one.md", (self.repo / "docs/EPIC-one.md").read_text() + "\nSee [facts](pages/a.md) and [web](https://x.io/a.md).\n")
        self.write("docs/pages/a.md", "# Facts A\n\nMore in [B](b.md#frag) and back to [one](../EPIC-one.md).\n")
        self.write("docs/pages/b.md", "No title here. Deeper: [C](../deep/c.md)\n")
        self.write("docs/deep/c.md", "# C\n")
        by = {n["path"]: n for n in self.log()["nodes"]}
        self.assertEqual([{"path": "docs/pages/a.md", "title": "Facts A", "via": "docs/EPIC-one.md"},
                          {"path": "docs/pages/b.md", "title": "b", "via": "docs/pages/a.md"},
                          {"path": "docs/deep/c.md", "title": "C", "via": "docs/pages/b.md"}], by["docs/EPIC-one.md"]["pages"])
        self.assertEqual([], by["docs/root.md"]["pages"])  # a child epic's pages stay with the child; epics are never pages

    def test_a_page_appears_under_several_epics(self) -> None:
        self.assertEqual(0, self.new("docs/EPIC-one.md", "docs/root.md", "one").returncode)
        for name in ("docs/root.md", "docs/EPIC-one.md"):
            self.write(name, (self.repo / name).read_text() + "\n[shared](shared.md)\n")
        self.write("docs/shared.md", "# Shared\n")
        by = {n["path"]: n for n in self.log()["nodes"]}
        self.assertEqual(["docs/shared.md"], [p["path"] for p in by["docs/root.md"]["pages"]])
        self.assertEqual(["docs/shared.md"], [p["path"] for p in by["docs/EPIC-one.md"]["pages"]])

    def test_orphan_pages_and_skips(self) -> None:
        self.write("docs/root.md", self.root_text + "\n[linked](linked.md)\n")
        self.write("docs/linked.md", "# Linked\n")
        self.write("docs/old-notes.md", "# Old notes\n")
        self.write("README.md", "# readme\n")
        self.write("CHANGELOG.md", "# changes\n")
        self.write("docs/archive/gone.md", "# gone\n")
        self.write("docs/handoffs/h.md", "# handoff\n")
        self.write("tests/t.md", "# t\n")
        self.write(".claude/skills/epic-spine/SKILL.md", "---\nname: x\n---\n")
        self.write(".claude/skills/epic-spine/references/r.md", "# r\n")
        log = self.log()
        self.assertEqual(["docs/old-notes.md"], log["orphan_pages"])
        self.assertEqual([], log["orphans"])  # pages are not orphan epics

    def test_looks_like_epic_needs_two_signals(self) -> None:
        self.write("docs/root.md", self.root_text + "\n[a](a.md) [b](b.md)\n")
        self.write("docs/a.md", PAGE_GOAL)  # linked page that reads as an epic
        self.write("docs/b.md", "# B\n\nStatus: draft\n")  # one signal only
        self.write("docs/c.md", "# C\n\n- [ ] one todo\n\nNext action: go\n")  # checkbox + next action, unlinked
        self.write("docs/d.md", "# D\n\nplain facts\n")
        log = self.log()
        self.assertEqual(["docs/a.md", "docs/c.md"], log["looks_like_epic"])
        self.assertEqual(["docs/c.md", "docs/d.md"], log["orphan_pages"])

    def test_plan_named_page_is_a_page_not_an_epic(self) -> None:
        self.write("docs/enforcement-plan.md", PAGE_GOAL)
        self.write("docs/PLAN-x.md", "# Plan\n")
        self.write("docs/E4-ONE-LOGGER.md", base.E4)
        log = self.log()
        self.assertEqual([], log["orphans"])
        self.assertEqual({"docs/enforcement-plan.md", "docs/PLAN-x.md", "docs/E4-ONE-LOGGER.md"}, set(log["orphan_pages"]))
        self.assertEqual(["docs/enforcement-plan.md"], log["looks_like_epic"])

    def test_stamp_or_spine_id_makes_an_epic(self) -> None:
        self.write("docs/stamped.md", "# EPIC-7: stamped, no id\n")
        self.write("docs/with-id.md", "# whatever\n\nSpine ID: with-id\n")
        self.write("docs/not-stamped.md", "# EPIC seven\n\nSpine type text: Spine ID: mid-line is not a header\n")
        self.assertEqual({"docs/stamped.md": "no Spine ID header", "docs/with-id.md": "not reachable from the root"}, {o["path"]: o["reason"] for o in self.log()["orphans"]})
        self.assertIn("docs/not-stamped.md", self.log()["orphan_pages"])

    def test_no_root_reports_no_pages(self) -> None:
        self.write("AGENTS.md", "Root spine: none. Read nothing.\n")
        self.write("docs/old-notes.md", PAGE_GOAL)
        log = self.log()
        self.assertEqual(([], []), (log["orphan_pages"], log["looks_like_epic"]))

    def test_existing_fields_keep_their_meaning(self) -> None:
        self.assertEqual(0, self.new("docs/EPIC-one.md", "docs/root.md", "one").returncode)
        node = {n["path"]: n for n in self.log()["nodes"]}["docs/EPIC-one.md"]
        for key in ("id", "path", "title", "parent", "type", "status", "rollup_status", "dod", "outcome", "current_state", "waiting_on", "children", "superseded_by"):
            self.assertIn(key, node)
        self.assertEqual(("", "docs/root.md", "ready"), (node["type"], node["parent"], node["status"]))  # no Spine Type is written; `type` stays deprecated


class ScaffoldAndValidatorTests(base.EpicLogCase):
    def test_scaffold_is_doctrine_2_without_spine_type(self) -> None:
        self.assertEqual(0, self.new("docs/EPIC-one.md", "docs/root.md", "one", "--purpose", "P").returncode)
        path = self.repo / "docs/EPIC-one.md"
        text = path.read_text()
        self.assertTrue(text.startswith("# EPIC-1: one\n"))
        for absent in ("Spine Type", "Spine dialect", "Ticket backend", "## Mission", "## Definition Of Done", "Doctrine:"):
            self.assertNotIn(absent, text)
        order = [text.index(h) for h in ("## Goal", "## Serves", "## Done means", "## Current State", "## Issue Ledger", "## Decisions", "## Operating Learnings")]
        self.assertEqual(sorted(order), order)
        self.assertIn("Status: ready", text)
        self.assertTrue(v.trackable(path)["trackable"], v.trackable(path))
        self.assertEqual(([], []), (v.validate_local(path).errors, v.validate_local(path).warnings[:0]))
        graph = subprocess.run([sys.executable, "-B", str(VALIDATOR_PATH), "--strict", "--graph", str(self.repo / "docs/root.md"), str(path)], capture_output=True, text=True)
        self.assertEqual(0, graph.returncode, graph.stdout)

    def test_registers_a_contributes_placeholder_in_the_parent_map(self) -> None:
        self.assertEqual(0, self.new("docs/EPIC-one.md", "docs/root.md", "one").returncode)
        row = next(line for line in (self.repo / "docs/root.md").read_text().splitlines() if "EPIC-one.md" in line)
        self.assertIn("<one sentence: what this adds to the parent's goal>", row)
        self.assertIn("| ready |", row)

    def test_spine_type_is_optional_and_ignored_when_present(self) -> None:
        self.assertEqual(0, self.new("docs/EPIC-one.md", "docs/root.md", "one").returncode)
        path = self.repo / "docs/EPIC-one.md"
        text = path.read_text()
        for variant in (text, text.replace("Spine profile: compact\n", "Spine profile: compact\nSpine Type: branch\n")):
            path.write_text(variant)
            self.assertEqual([], v.validate_local(path).errors)
        self.assertEqual("branch", v.lineage(v.parse_fields(text)))  # inferred from the linked Root/Parent spine
        self.assertEqual("root", v.lineage({"Root spine": "self", "Parent spine": "none"}))
        self.assertEqual("", v.lineage({"Root spine": "none | <link>", "Parent spine": "<link>"}))
        self.assertEqual("root", v.lineage({"Spine Type": "root"}))  # an explicit old value is still read

    def test_done_means_and_goal_headings_validate_like_the_old_ones(self) -> None:
        root = self.repo / "docs/root.md"
        text = root.read_text().replace("## Mission", "## Goal").replace("## Definition Of Done", "## Done means")
        root.write_text(text)
        result = v.trackable(root)
        self.assertTrue(result["trackable"], result)
        self.assertEqual([], v.validate_local(root).errors)
        root.write_text(text.replace("- [ ] R-1 purpose met", "purpose met"))
        self.assertIn("criteria `- [ ] ID text` under ## Done means", v.trackable(root)["missing"])


class PreCommitDoctrineTests(base.EpicLogCase):
    def setUp(self) -> None:
        super().setUp()
        self.git("init", "-q")
        tree_gate.install(base.agents_block, self.repo, "docs/root.md")
        self.git("add", "-A")
        self.assertEqual(0, self.git("commit", "--no-verify", "-m", "base").returncode)  # history before the hook: an old-style root

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.repo, capture_output=True, text=True)

    def commit(self, name: str, text: str | None = None) -> subprocess.CompletedProcess:
        if text is not None:
            self.write(name, text)
        self.git("add", "-A")
        return self.git("commit", "-m", "x")

    def scaffold(self, name: str = "docs/EPIC-one.md") -> str:
        self.assertEqual(0, self.new(name, "docs/root.md", "one", "--purpose", "P").returncode)
        return (self.repo / name).read_text()

    def test_new_epic_missing_sections_is_blocked_then_passes(self) -> None:
        text = self.scaffold()
        for gap, cut in (("serves", text.replace("## Serves\n\n[EPIC-0: Root](root.md): <one sentence: how this serves its parent>\n\n", "")),
                         ("done_means", text.replace("## Done means\n\n", "## Notes\n\n")),
                         ("goal", text.replace("## Goal\n\nP\n\n", "")), ("status", text.replace("Status: ready", "Status:"))):
            with self.subTest(gap=gap):
                self.git("reset", "-q")
                blocked = self.commit("docs/EPIC-one.md", cut)
                self.assertNotEqual(0, blocked.returncode, blocked.stderr)
                self.assertIn(f"docs/EPIC-one.md: epic is missing {gap}", blocked.stderr)
        self.git("reset", "-q")
        ok = self.commit("docs/EPIC-one.md", text)
        self.assertEqual(0, ok.returncode, ok.stderr)
        self.assertNotIn("docs/EPIC-one.md: epic is missing", ok.stderr)

    def test_new_epic_title_is_required(self) -> None:
        text = self.scaffold().replace("# EPIC-1: one", "# EPIC: one")
        blocked = self.commit("docs/EPIC-one.md", text)
        self.assertNotEqual(0, blocked.returncode)
        self.assertIn("epic is missing title", blocked.stderr)

    def test_existing_epic_only_warns(self) -> None:
        text = self.scaffold()
        self.assertEqual(0, self.commit("docs/EPIC-one.md", text).returncode)
        long = "| a | " + "x" * 201 + " |\n"
        edited = text.replace("## Serves\n\n[EPIC-0: Root](root.md): <one sentence: how this serves its parent>\n\n", "") + long + "\nfiller\n" * 160
        done = self.commit("docs/EPIC-one.md", edited)
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("docs/EPIC-one.md: epic is missing serves", done.stderr)
        self.assertIn("over the size budget", done.stderr)
        self.assertIn("(advisory)", done.stderr)

    def test_existing_old_style_root_passes_with_advisory(self) -> None:
        self.write("docs/root.md", self.root_text.replace("# EPIC-0: Root", "# EPIC: Root"))
        done = self.commit("docs/root.md")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("docs/root.md: epic is missing title", done.stderr)

    def test_doctrine_notes_block_only_when_new(self) -> None:
        import pre_commit
        text = "# EPIC-3: t\n\n## Goal\n\nG\n"
        self.assertEqual((True, True), (pre_commit.doctrine_notes("a.md", text, True, {})[0], "missing serves, done_means, status" in pre_commit.doctrine_notes("a.md", text, True, {})[1]))
        old = pre_commit.doctrine_notes("a.md", text, False, {})
        self.assertEqual((False, True), (old[0], old[1].endswith("(advisory)")))
        self.assertEqual((False, ""), pre_commit.doctrine_notes("a.md", self.scaffold(), True, {}))

    def test_plan_page_is_not_blocked_and_gets_page_advisories(self) -> None:
        done = self.commit("docs/enforcement-plan.md", PAGE_GOAL)
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("docs/enforcement-plan.md: looks like an epic", done.stderr)
        self.assertIn("docs/enforcement-plan.md: orphan page", done.stderr)

    def test_linked_plain_page_is_silent(self) -> None:
        self.write("docs/root.md", self.root_text + "\n[facts](facts.md)\n")
        done = self.commit("docs/facts.md", "# Facts\n\nplain\n")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertNotIn("orphan page", done.stderr)
        self.assertNotIn("looks like an epic", done.stderr)

    def test_superseded_by_outside_the_repo_blocks_without_raising(self) -> None:
        text = self.scaffold().replace("Integration branch: main\n", "Integration branch: main\nSuperseded by: [x](../../outside.md)\n")
        blocked = self.commit("docs/EPIC-one.md", text)
        self.assertNotEqual(0, blocked.returncode)
        self.assertIn("is not an existing goal doc", blocked.stderr)
        self.assertNotIn("Traceback", blocked.stderr)


if __name__ == "__main__":
    unittest.main()
