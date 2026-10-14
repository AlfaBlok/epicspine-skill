from __future__ import annotations

import functools
import importlib.util
import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

GATE = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts" / "url_gate.py"
HOST_VARS = ("EPICSPINE_ARTIFACT_HOST", "EPICSPINE_ARTIFACT_BIND")
# The gate runs as a subprocess, so `artifact_host.resolve` cannot be patched there:
# an explicit loopback host is the equivalent of resolve() returning the loopback dict.
LOOPBACK = {"EPICSPINE_ARTIFACT_HOST": "127.0.0.1"}


def hermetic_env(env: dict | None = None) -> dict:
    """Process env minus the artifact-host vars, then the test's own."""
    return {**{k: v for k, v in os.environ.items() if k not in HOST_VARS}, **(env or {})}


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
            capture_output=True, timeout=30, env=hermetic_env({**LOOPBACK, **(env or {})}))
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



class UrlGateArtifactHostTest(unittest.TestCase):
    """Non-loopback host (explicit or auto-detected): tailnet host accepted, loopback-only is missing."""

    def setUp(self) -> None:
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        for var in HOST_VARS:
            os.environ.pop(var, None)

    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("url_gate_t", GATE)
        sys.path.insert(0, str(GATE.parent))
        cls.gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.gate)

    def decide(self, text: str, ok: bool = True) -> str | None:
        info = {"host": "vps.tail.ts.net", "bind": "100.64.0.5"}
        with mock.patch.object(self.gate.artifact_host, "resolve", return_value=info), \
                mock.patch.object(self.gate, "status_ok", return_value=ok):
            return self.gate.decide(text)

    def test_tailnet_url_allows(self) -> None:
        self.assertIsNone(self.decide("Done: /tmp/x.html\n\nhttp://vps.tail.ts.net:8091/x.html\n"))
        self.assertIsNone(self.decide("http://100.64.0.5:8091/x.html"))

    def test_localhost_only_blocks_naming_host(self) -> None:
        for text in ("See http://127.0.0.1:8091/x.html", "Open http://localhost:8091/x.html",
                     "Open /tmp/x.html"):
            with self.subTest(text=text):
                reason = self.decide(text)
                self.assertIn("http://vps.tail.ts.net:<port>/<file>", reason)

    def test_tailnet_url_must_serve(self) -> None:
        self.assertIn("not serving", self.decide("http://vps.tail.ts.net:8091/x.html", ok=False))

    def test_tailnet_wins_over_localhost(self) -> None:
        self.assertIsNone(self.decide("http://127.0.0.1:1/x.html and http://vps.tail.ts.net:2/x.html"))

    def test_auto_detect_end_to_end(self) -> None:
        """Headless + Tailscale with env unset: resolve() (not mocked) yields the tailnet host."""
        def fake_run(*cmd: str) -> str:
            return '{"Self": {"DNSName": "vps.tail.ts.net."}}' if cmd[1] == "status" else "100.64.0.5\n"
        env = {k: v for k, v in os.environ.items() if k != "EPICSPINE_ARTIFACT_HOST"}
        ah = self.gate.artifact_host
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(ah.sys, "platform", "linux"), \
                mock.patch.object(ah, "_run", fake_run), mock.patch.object(self.gate, "status_ok", return_value=True):
            os.environ.pop("DISPLAY", None)
            self.assertIn("http://vps.tail.ts.net:<port>", self.gate.decide("See http://127.0.0.1:8091/x.html"))
            self.assertIsNone(self.gate.decide("http://vps.tail.ts.net:8091/x.html"))
            os.environ["DISPLAY"] = ":0"
            self.assertIsNone(self.gate.decide("http://127.0.0.1:8091/x.html"))

    def test_subprocess_literal_host_blocks_loopback_only(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-B", str(GATE)], text=True, capture_output=True, timeout=30,
            env=hermetic_env({"EPICSPINE_ARTIFACT_HOST": "100.64.0.5"}),
            input=json.dumps({"session_id": self.id(), "last_assistant_message":
                              "Open http://127.0.0.1:8091/x.html"}))
        self.assertIn("100.64.0.5", json.loads(proc.stdout)["reason"])


if __name__ == "__main__":
    unittest.main()
