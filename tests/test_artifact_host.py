from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts" / "artifact_host.py"
SPEC = importlib.util.spec_from_file_location("artifact_host_t", SCRIPT)
ah = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ah)

STATUS = '{"Self": {"DNSName": "vps-a9-1.taild81fbb.ts.net."}}'
LOCAL = {"host": "127.0.0.1", "bind": "127.0.0.1"}


def fake_ts(ip: str = "100.104.206.10\nfd7a::1\n"):
    def run(*cmd: str) -> str:
        return STATUS if cmd[1] == "status" else ip
    return run


class ArtifactHostTest(unittest.TestCase):
    def setUp(self) -> None:
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        for var in ("EPICSPINE_ARTIFACT_HOST", "EPICSPINE_ARTIFACT_BIND"):
            os.environ.pop(var, None)

    def resolve(self, env: dict) -> tuple[dict, str]:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            return ah.resolve(env), err.getvalue()

    def test_unset_or_empty_is_loopback(self) -> None:
        for env in ({}, {"EPICSPINE_ARTIFACT_HOST": " "}):
            self.assertEqual(self.resolve(env), (LOCAL, ""))

    def test_tailscale(self) -> None:
        with mock.patch.object(ah, "_run", fake_ts()):
            info, err = self.resolve({"EPICSPINE_ARTIFACT_HOST": "tailscale"})
        self.assertEqual(info, {"host": "vps-a9-1.taild81fbb.ts.net", "bind": "100.104.206.10"})
        self.assertEqual(err, "")

    def test_literal_host_resolved(self) -> None:
        with mock.patch.object(ah.socket, "gethostbyname", return_value="10.1.2.3"):
            info, _ = self.resolve({"EPICSPINE_ARTIFACT_HOST": "box.lan"})
        self.assertEqual(info, {"host": "box.lan", "bind": "10.1.2.3"})

    def test_bind_override(self) -> None:
        with mock.patch.object(ah, "_run", fake_ts()):
            info, _ = self.resolve({"EPICSPINE_ARTIFACT_HOST": "tailscale",
                                    "EPICSPINE_ARTIFACT_BIND": "100.64.0.9"})
        self.assertEqual(info["bind"], "100.64.0.9")

    def test_disallowed_bind_falls_back(self) -> None:
        for bind in ("0.0.0.0", "8.8.8.8"):
            with self.subTest(bind=bind), mock.patch.object(ah.socket, "gethostbyname", return_value=bind):
                info, err = self.resolve({"EPICSPINE_ARTIFACT_HOST": "box.example"})
                self.assertEqual(info, LOCAL)
                self.assertIn(bind, err)

    def test_failed_lookup_falls_back(self) -> None:
        with mock.patch.object(ah, "_run", side_effect=FileNotFoundError("tailscale")):
            info, err = self.resolve({"EPICSPINE_ARTIFACT_HOST": "tailscale"})
        self.assertEqual(info, LOCAL)
        self.assertIn("using 127.0.0.1", err)

    def test_allowed_ranges(self) -> None:
        for ip in ("127.0.0.1", "100.104.206.10", "10.0.0.1", "172.20.1.1", "192.168.1.1"):
            self.assertTrue(ah.allowed(ip), ip)
        for ip in ("0.0.0.0", "8.8.8.8", "100.128.0.1", "172.32.0.1"):
            self.assertFalse(ah.allowed(ip), ip)

    def test_cli_json_line(self) -> None:
        out = subprocess.run([sys.executable, "-B", str(SCRIPT), "--port", "8091"], text=True,
                             capture_output=True, env={"PATH": ""}, timeout=30).stdout
        self.assertEqual(
            out.strip(),
            '{"host": "127.0.0.1", "bind": "127.0.0.1", "port": 8091, "base": "http://127.0.0.1:8091"}')


if __name__ == "__main__":
    unittest.main()
