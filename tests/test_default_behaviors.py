from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).parents[1]
VENDOR_RE = re.compile(r"deepseek|opencode", re.I)
SHIPPED = (
    "skill/epic-spine/SKILL.md",
    "skill/epic-spine/assets/agents-block.md",
    "skill/epic-spine/references/roles-and-dispatch.md",
)


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


class DefaultBehaviorsTest(unittest.TestCase):
    def between(self, text: str, start: str, end: str) -> str:
        self.assertIn(start, text)
        body = text[text.index(start) + len(start):]
        self.assertIn(end, body)
        return body[: body.index(end)]

    def agents_block(self) -> str:
        return self.between(read("AGENTS.md"), "<!-- epicspine:begin", "<!-- epicspine:end -->")

    def card(self) -> str:
        return self.between(read("skill/epic-spine/SKILL.md"), "## Default Behaviors", "## Bind Path")

    def default_table(self) -> str:
        return self.between(
            read("skill/epic-spine/references/roles-and-dispatch.md"),
            "## Built-In Default", "## Resolution Order")

    def test_a_no_hardwired_vendor_model(self) -> None:
        for rel in SHIPPED:
            text = read(rel)
            self.assertNotRegex(text, VENDOR_RE, rel)

    def test_a2_ask_and_record_and_defer_to_spine(self) -> None:
        for region in (self.agents_block(), self.card()):
            self.assertIn("Dispatch profile:", region)
            self.assertIn("ask once", region)
            self.assertIn("record", region)
            self.assertIn("~/.agents/epicspine-profile.md", region)
        self.assertIn("lower-cost", self.default_table())
        refs = read("skill/epic-spine/references/roles-and-dispatch.md")
        self.assertIn("## Unset Or Ask", refs)
        self.assertIn("ask the user once", refs)
        self.assertIn("~/.agents/epicspine-profile.md", refs)
        self.assertIn("not the repo", refs)
        self.assertIn("optional override only", refs)
        self.assertIn("~/.agents/epicspine-profile.md", read("skill/epic-spine/assets/global-block.md"))

    def test_b_manager_never_implements(self) -> None:
        self.assertIn("never implements", self.agents_block().lower())
        self.assertIn("never implements", self.card().lower())

    def test_c_worktree_ff_only_revert_on_red(self) -> None:
        card = self.agents_block() + self.card()
        git = read("skill/epic-spine/references/git-doctrine.md")
        for text in (card, git):
            self.assertRegex(text, r"worktree")
            self.assertIn("ff-only", text.lower())
            self.assertRegex(text, r"revert")

    def test_d_binding_names_role_and_learnings(self) -> None:
        block = self.agents_block().lower()
        self.assertIn("whatever the message", block)
        self.assertIn("delivery manager · epicspine · learnings in force:", block)
        self.assertIn("learnings in force:", block)
        self.assertIn("final answer", block)

    def test_e_always_learnings_l1_to_l8_in_order(self) -> None:
        always = self.between(read("docs/EPIC-2-OPERATING-SYSTEM.md"), "**Always**", "**Scoped index**")
        ids = [int(n) for n in re.findall(r"L-(\d+)\s*\|", always)]
        # 1..8 present, in order; later scoped/Always additions may append after 8.
        self.assertEqual(ids[:8], list(range(1, 9)))

    def test_f_adopted_learnings_l9_to_l11(self) -> None:
        always = self.between(read("docs/EPIC-2-OPERATING-SYSTEM.md"), "**Always**", "**Scoped index**")
        ids = [int(n) for n in re.findall(r"L-(\d+)\s*\|", always)]
        for n in (9, 10, 11):
            self.assertIn(n, ids)

    def test_g_adopted_doctrine_phrases(self) -> None:
        refs = read("skill/epic-spine/references/roles-and-dispatch.md") + read(
            "skill/epic-spine/references/role-protocols.md"
        )
        self.assertIn("decision", self.card().lower())
        self.assertIn("ready frontier", refs.lower())
        self.assertIn("two independent axes", refs.lower())


if __name__ == "__main__":
    unittest.main()
