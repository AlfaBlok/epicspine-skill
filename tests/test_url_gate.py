from __future__ import annotations

import functools
import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

GATE = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts" / "url_gate.py"


class UrlGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="epicspine-gate-")
        (Path(cls._tmp.name) / "report.html").write_text("<p>hi</p>")

        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args, **kwargs) -> None:
                pass

        handler = functools.partial(Quiet, directory=cls._tmp.name)
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls._tmp.cleanup()

    def gate(self, message: str | None = None, *, raw: str | None = None,
             env: dict | None = None, **extra) -> tuple[int, dict | None]:
        payload = raw if raw is not None else json.dumps(
            {"session_id": self.id(), "hook_event_name": "Stop",
             "last_assistant_message": message, **extra})
        proc = subprocess.run(
            [sys.executable, "-B", str(GATE)], input=payload, text=True,
            capture_output=True, timeout=30, env={**os.environ, **(env or {})})
        out = proc.stdout.strip()
        return proc.returncode, (json.loads(out) if out else None)

    def assertBlocks(self, message: str, **kw) -> dict:
        code, out = self.gate(message, **kw)
        self.assertEqual(code, 0)
        self.assertIsNotNone(out, message)
        self.assertEqual(out["decision"], "block")
        return out

    def assertAllows(self, *args, **kw) -> None:
        code, out = self.gate(*args, **kw)
        self.assertEqual((code, out), (0, None))

    def url(self, name: str = "report.html") -> str:
        return f"http://127.0.0.1:{self.port}/{name}"

    def test_path_only_html_blocks(self) -> None:
        out = self.assertBlocks("Done. Open /tmp/x.html in your browser.")
        self.assertIn("served URL", out["reason"])
        self.assertIn("/tmp/x.html", out["reason"])

    def test_file_url_blocks(self) -> None:
        self.assertBlocks("Report: file:///tmp/out/report.html")

    def test_other_visual_extensions_block(self) -> None:
        for name in ("out/chart.svg", "docs/shot.png", "out/report.pdf"):
            with self.subTest(name=name):
                self.assertBlocks(f"Wrote {name}.")

    def test_bare_filename_needs_open_word(self) -> None:
        self.assertAllows("I edited index.html and fixed the header.")
        self.assertBlocks("Please open report.html to see it.")

    def test_reachable_url_allows(self) -> None:
        self.assertAllows(f"Done. Also wrote /tmp/x.html.\n\n{self.url()}\n")

    def test_markdown_link_url_allows(self) -> None:
        self.assertAllows(f"[report]({self.url()})")

    def test_missing_url_404_blocks(self) -> None:
        out = self.assertBlocks(f"See {self.url('nope.html')}")
        self.assertIn("nope.html", out["reason"])

    def test_unreachable_url_blocks(self) -> None:
        self.assertBlocks("See http://127.0.0.1:9/x.html")

    def test_localhost_url_checked(self) -> None:
        self.assertAllows(f"http://localhost:{self.port}/report.html")

    def test_non_visual_paths_allow(self) -> None:
        self.assertAllows("Changed src/app.py, docs/README.md, data/out.json and a.csv.")

    def test_remote_urls_and_globs_allow(self) -> None:
        self.assertAllows("See https://example.com/page.html and the *.html glob.")

    def test_fenced_code_ignored(self) -> None:
        self.assertAllows("Diff:\n```html\n<img src=\"img/a.png\">\n<a href=\"/x/y.html\">\n```\n")

    def test_loop_cap(self) -> None:
        msg = "Open /tmp/x.html"
        self.assertBlocks(msg, stop_hook_active=False)
        self.assertBlocks(msg, stop_hook_active=True)
        self.assertAllows(msg, stop_hook_active=True)
        # cap resets: a fresh turn blocks again
        self.assertBlocks(msg, stop_hook_active=False)

    def test_transcript_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "t.jsonl"
            rows = [
                {"type": "assistant", "message": {"content": [{"type": "text", "text": "ok"}]}},
                {"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": "x"},
                    {"type": "text", "text": "Open /tmp/x.html"}]}},
            ]
            path.write_text("\n".join(json.dumps(r) for r in rows))
            self.assertBlocks("", transcript_path=str(path))

    def test_malformed_stdin_allows(self) -> None:
        for raw in ("not json", "", "[1]", '{"last_assistant_message": 5}'):
            with self.subTest(raw=raw):
                self.assertAllows(raw=raw)

    def test_env_off_allows(self) -> None:
        self.assertAllows("Open /tmp/x.html", env={"EPICSPINE_URL_GATE": "off"})


if __name__ == "__main__":
    unittest.main()
