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

    def resolve(self, env: dict, platform: str = "linux") -> tuple[dict, str]:
        err = io.StringIO()
        with contextlib.redirect_stderr(err), mock.patch.object(ah.sys, "platform", platform):
            return ah.resolve(env), err.getvalue()

    def test_headless_with_tailscale_auto_uses_tailnet(self) -> None:
        for env in ({}, {"EPICSPINE_ARTIFACT_HOST": " "}, {"EPICSPINE_ARTIFACT_HOST": "auto"},
                    {"XDG_SESSION_TYPE": "tty"}):
            with self.subTest(env=env), mock.patch.object(ah, "_run", fake_ts()):
                self.assertEqual(self.resolve(env),
                                 ({"host": "vps-a9-1.taild81fbb.ts.net", "bind": "100.104.206.10"}, ""))

    def test_headless_without_tailscale_is_silent_loopback(self) -> None:
        for fail in (FileNotFoundError("tailscale"), subprocess.TimeoutExpired("tailscale", 3)):
            with self.subTest(fail=type(fail).__name__), mock.patch.object(ah, "_run", side_effect=fail):
                self.assertEqual(self.resolve({}), (LOCAL, ""))
        with mock.patch.object(ah, "_run", fake_ts("8.8.8.8\n")):
            self.assertEqual(self.resolve({}), (LOCAL, ""))

    def test_desktop_is_loopback_even_with_tailscale(self) -> None:
        cases = [({"DISPLAY": ":0"}, "linux"), ({"WAYLAND_DISPLAY": "wayland-0"}, "linux"),
                 ({"XDG_SESSION_TYPE": "Wayland"}, "linux"), ({"XDG_SESSION_TYPE": "x11"}, "linux"),
                 ({}, "darwin"), ({}, "win32")]
        for env, platform in cases:
            with self.subTest(env=env, platform=platform), \
                    mock.patch.object(ah, "_run", side_effect=fake_ts()) as run:
                self.assertEqual(self.resolve(env, platform), (LOCAL, ""))
                run.assert_not_called()

    def test_local_forces_loopback(self) -> None:
        for value in ("local", "127.0.0.1"):
            with self.subTest(value=value), mock.patch.object(ah, "_run", side_effect=fake_ts()) as run:
                self.assertEqual(self.resolve({"EPICSPINE_ARTIFACT_HOST": value}), (LOCAL, ""))
                run.assert_not_called()

    def test_explicit_tailscale_ignores_desktop_detection(self) -> None:
        with mock.patch.object(ah, "_run", fake_ts()):
            info, _ = self.resolve({"EPICSPINE_ARTIFACT_HOST": "tailscale", "DISPLAY": ":0"}, "darwin")
        self.assertEqual(info["bind"], "100.104.206.10")

    def test_auto_honours_bind_override(self) -> None:
        with mock.patch.object(ah, "_run", fake_ts()):
            info, _ = self.resolve({"EPICSPINE_ARTIFACT_BIND": "100.64.0.9"})
        self.assertEqual(info["bind"], "100.64.0.9")

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
                             capture_output=True, env={"PATH": "", "DISPLAY": ":0"}, timeout=30).stdout
        self.assertEqual(
            out.strip(),
            '{"host": "127.0.0.1", "bind": "127.0.0.1", "port": 8091, "base": "http://127.0.0.1:8091"}')


if __name__ == "__main__":
    unittest.main()
