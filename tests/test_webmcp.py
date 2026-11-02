"""WebMCP on epicspine.dev (EPIC-10 E10-S1): the home page registers three read-only tools.

The static checks always run. When node is on PATH, the page's WebMCP script runs against a
stubbed ``document.modelContext`` and a minimal DOM built from index.html itself.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

INDEX = Path(__file__).parents[1] / "index.html"
TOOLS = ("get_install_command", "list_sections", "go_to_section")


def webmcp_script(html: str) -> str:
    scripts = [s for s in re.findall(r"<script>(.*?)</script>", html, re.S) if "modelContext" in s]
    assert len(scripts) == 1, "expected exactly one inline WebMCP <script>"
    return scripts[0]


class Page(HTMLParser):
    """Sections (id, heading, first paragraph, text) and the install lines, as a browser sees them."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[dict] = []
        self.install = ""
        self.stack: list[str] = []
        self.cur: dict | None = None
        self.grab: str | None = None
        self.in_install = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and a.get("id"):
            self.cur = {"id": a["id"], "heading": "", "p": "", "text": ""}
            self.sections.append(self.cur)
        elif self.cur and tag in ("h1", "h2") and not self.cur["heading"]:
            self.grab = "heading"
        elif self.cur and tag == "p" and not self.cur["p"]:
            self.grab = "p"
        if a.get("id") == "install-cmd":
            self.in_install = True
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "section":
            self.cur = None
        if tag in ("h1", "h2", "p"):
            self.grab = None
        if tag == "pre":
            self.in_install = False

    def handle_data(self, data):
        if self.cur:
            self.cur["text"] += data
            if self.grab:
                self.cur[self.grab] += data
        if self.in_install:
            self.install += data


NODE_HARNESS = r"""
const vm = require("vm");
const [script, page, mode] = [process.argv[1], JSON.parse(process.argv[2]), process.argv[3]];
const tools = {}; let scrolled = null;
const el = (t) => ({ textContent: t });
const sections = page.sections.map((s) => ({
  id: s.id, textContent: s.text,
  querySelector: (q) => (q.includes("h1") ? (s.heading ? el(s.heading) : null) : (s.p ? el(s.p) : null)),
  scrollIntoView() { scrolled = s.id; },
}));
const mc = { registerTool: async (t) => { tools[t.name] = t; } };
const document = {
  querySelectorAll: () => sections,
  getElementById: (id) => (id === "install-cmd" ? el(page.install) : sections.find((s) => s.id === id) || null),
};
const navigator = {};
if (mode === "document") document.modelContext = mc;
if (mode === "navigator") navigator.modelContext = mc;
const errors = [];
const console = { error: (...a) => errors.push(a.join(" ")), warn: (...a) => errors.push(a.join(" ")), log() {} };
vm.runInNewContext(script, { document, navigator, console, Promise });
setTimeout(async () => {
  const out = { names: Object.keys(tools).sort(), errors, calls: {} };
  if (tools.get_install_command) {
    out.tools = Object.fromEntries(Object.values(tools).map((t) => [t.name, { description: t.description, inputSchema: t.inputSchema, annotations: t.annotations }]));
    out.calls.install = await tools.get_install_command.execute({}, {});
    out.calls.list = await tools.list_sections.execute({}, {});
    out.calls.go = await tools.go_to_section.execute({ id: "install" }, {});
    out.scrolled = scrolled;
    try { await tools.go_to_section.execute({ id: "nope" }, {}); out.calls.bad = "no error"; }
    catch (e) { out.calls.bad = String(e.message); }
  }
  process.stdout.write(JSON.stringify(out));
}, 0);
"""


class WebMCPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX.read_text()
        cls.script = webmcp_script(cls.html)
        cls.page = Page()
        cls.page.feed(cls.html)

    def test_script_is_feature_detected_read_only_and_names_the_tools(self) -> None:
        s = self.script
        self.assertIn("document.modelContext || navigator.modelContext", s)
        self.assertRegex(s, r"if \(!mc[^)]*\) \{ return; \}")
        self.assertIn("try {", s)
        self.assertIn("readOnlyHint: true", s)
        for name in TOOLS:
            self.assertIn(f'name: "{name}"', s)
        for bad in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "http://", "https://"):
            self.assertNotIn(bad, s, f"WebMCP script must not send data anywhere ({bad})")

    def run_node(self, mode: str) -> dict:
        node = shutil.which("node")
        if not node:
            self.skipTest("node not on PATH")
        page = {"sections": self.page.sections, "install": self.page.install}
        out = subprocess.run([node, "-e", NODE_HARNESS, self.script, json.dumps(page), mode],
                             capture_output=True, text=True, timeout=30, check=True)
        return json.loads(out.stdout)

    def test_no_model_context_does_nothing(self) -> None:
        out = self.run_node("none")
        self.assertEqual(out["names"], [])
        self.assertEqual(out["errors"], [])

    def test_navigator_alias_still_registers(self) -> None:
        self.assertEqual(self.run_node("navigator")["names"], sorted(TOOLS))

    def test_tools_read_the_page(self) -> None:
        out = self.run_node("document")
        self.assertEqual(out["names"], sorted(TOOLS))
        self.assertEqual(out["errors"], [])
        for name, t in out["tools"].items():
            self.assertEqual(t["annotations"], {"readOnlyHint": True}, name)
            self.assertIn("EpicSpine", t["description"], name)
            self.assertIn("goal tree", t["description"], name)

        cmd = out["calls"]["install"]["command"]
        self.assertTrue(cmd.startswith("git clone https://github.com/AlfaBlok/epicspine-skill"), cmd)
        self.assertTrue(cmd.endswith("python3 scripts/agents_block.py install-global"), cmd)
        self.assertNotIn("$ ", cmd)
        self.assertTrue(out["calls"]["install"]["does"])

        ids = [s["id"] for s in self.page.sections]
        for i in ("why", "plan", "memory", "loop", "roles", "install", "next"):
            self.assertIn(i, ids)
        listed = out["calls"]["list"]["sections"]
        self.assertEqual([s["id"] for s in listed], ids)
        why = next(s for s in listed if s["id"] == "why")
        self.assertEqual(why["heading"], "Agents lose the plot between chats.")
        self.assertEqual(why["firstParagraph"], "EpicSpine moves the plan out of the chat and into a file.")

        self.assertEqual(out["tools"]["go_to_section"]["inputSchema"]["properties"]["id"]["enum"], ids)
        self.assertEqual(out["tools"]["go_to_section"]["inputSchema"]["required"], ["id"])
        go = out["calls"]["go"]
        self.assertEqual(out["scrolled"], "install")
        self.assertEqual(go["heading"], "Install once per machine.")
        self.assertIn("agents_block.py install-global", go["text"])
        self.assertIn("Unknown section id", out["calls"]["bad"])


if __name__ == "__main__":
    unittest.main()
