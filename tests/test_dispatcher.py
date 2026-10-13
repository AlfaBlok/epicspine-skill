from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


disp = load("dispatcher_t", ROOT / "skill/epic-spine/scripts/dispatcher.py")
adapter = load("t3_seat_pool_t", ROOT / "examples/dispatchers/t3_seat_pool.py")

FAKE = """import json, sys, time
a = sys.argv[1:]
mode = {mode!r}
if mode == "exit": sys.exit(3)
if mode == "text": print("hello"); sys.exit(0)
if mode == "sleep": time.sleep(5)
if a[0] == "status": print(json.dumps({{"name": "seat pool", "capacity": 2, "available": 1, "x": 1}}))
elif a[0] == "pick":
    if mode == "busy": print(json.dumps({{"id": None, "reason": "all busy"}}))
    elif mode == "badvia": print(json.dumps({{"id": "s", "via": "magic"}}))
    elif mode == "nofield": print(json.dumps({{"id": "s", "via": "t3_delegate_task"}}))
    else: print(json.dumps({{"id": "seat1", "via": "t3_delegate_task", "providerInstanceId": "claudeAgent_seat1", "args": a[1:]}}))
else: print(json.dumps({{"ok": True, "args": a[1:]}}))
"""


class DispatcherTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="epicspine-d-")
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_d(self, *args: str, mode: str | None = "ok", timeout: int | None = None):
        env = {"EPICSPINE_DISPATCHER": ""}
        if mode:
            script = self.tmp / "fake.py"
            script.write_text(FAKE.format(mode=mode))
            env["EPICSPINE_DISPATCHER"] = f"{sys.executable} {script}"
        out = io.StringIO()
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out), \
                mock.patch.object(disp, "TIMEOUT", timeout or 20):
            code = disp.main(["--repo", str(self.repo), *args])
        return code, out.getvalue()

    def test_unset_inactive(self) -> None:
        code, out = self.run_d("status", mode=None)
        self.assertEqual((code, json.loads(out)), (0, {"active": False}))
        self.assertEqual(self.run_d("bind", mode=None), (0, ""))

    def test_status_and_bind(self) -> None:
        code, out = self.run_d("status")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["capacity"], 2)
        self.assertEqual(self.run_d("bind"), (0, " · dispatch: seat pool (2 seats)\n"))

    def test_pick_valid_and_task(self) -> None:
        code, out = self.run_d("pick", "--task", "do x")
        data = json.loads(out)
        self.assertEqual((code, data["id"], data["via"]), (0, "seat1", "t3_delegate_task"))
        self.assertEqual(data["args"], ["--task", "do x"])

    def test_pick_null(self) -> None:
        code, out = self.run_d("pick", mode="busy")
        self.assertEqual((code, json.loads(out)["id"]), (0, None))

    def test_failures_error_and_fallback_bind(self) -> None:
        for mode in ("badvia", "nofield"):
            code, out = self.run_d("pick", mode=mode)
            self.assertEqual(code, 2, mode)
            self.assertIn("error", json.loads(out))
        for mode in ("exit", "text"):
            code, out = self.run_d("status", mode=mode)
            self.assertEqual(code, 2, mode)
            self.assertIn("error", json.loads(out))
            self.assertEqual(self.run_d("bind", mode=mode),
                             (0, " · dispatch: unavailable → native subagent\n"))

    def test_timeout(self) -> None:
        code, out = self.run_d("status", mode="sleep", timeout=1)
        self.assertEqual(code, 2)
        self.assertIn("timed out", json.loads(out)["error"])

    def test_missing_command(self) -> None:
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"EPICSPINE_DISPATCHER": "/nonexistent/x"}), contextlib.redirect_stdout(out):
            self.assertEqual(disp.main(["status"]), 2)

    def test_local_only_opt_out(self) -> None:
        (self.repo / "AGENTS.md").write_text("Root spine: docs/S.md. x\n")
        (self.repo / "docs").mkdir()
        (self.repo / "docs/S.md").write_text("Dispatch profile: local-only\n")
        code, out = self.run_d("pick")
        self.assertEqual(json.loads(out), {"active": False})
        self.assertEqual(self.run_d("bind"), (0, ""))
        (self.repo / "docs/S.md").write_text("Dispatch profile: default\n")
        self.assertEqual(json.loads(self.run_d("pick")[1])["id"], "seat1")
        (self.repo / "AGENTS.md").write_text("Dispatch profile: local-only\n")
        self.assertEqual(json.loads(self.run_d("pick")[1]), {"active": False})

    def test_done_passthrough(self) -> None:
        code, out = self.run_d("done", "seat1", "--fail", "--signal", "limit hit")
        data = json.loads(out)
        self.assertEqual((code, data["ok"]), (0, True))
        self.assertEqual(data["args"], ["seat1", "--fail", "--signal", "limit hit"])


class AdapterTest(unittest.TestCase):
    def test_translates_broker(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            b = Path(d) / "broker.py"
            b.write_text(
                "import sys, json\n"
                "c = sys.argv[1]\n"
                "if c == 'pick': print(json.dumps({'seat': 'seat2', 'providerInstanceId': 'claudeAgent_seat2'}) if not __import__('os').path.exists(__file__ + '.full') else json.dumps({'seat': None, 'providerInstanceId': None}))\n"
                "elif c == 'done': open(__file__ + '.log', 'w').write(' '.join(sys.argv[2:]))\n"
                "else: print(json.dumps({'seats': {'seat1': {'in_flight': 1}, 'seat2': {'in_flight': 0}, 'seat3': {'maxed_until': 'x'}}}))\n")

            def call(*a: str) -> dict:
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    self.assertEqual(adapter.main(["--broker", str(b), *a]), 0)
                return json.loads(out.getvalue())

            self.assertEqual(call("status"), {"name": "seat pool", "capacity": 3, "available": 1})
            self.assertEqual(call("pick", "--task", "t"), {
                "id": "seat2", "via": "t3_delegate_task", "providerInstanceId": "claudeAgent_seat2"})
            self.assertEqual(call("done", "seat2", "--fail", "--signal", "x"), {"ok": True})
            self.assertEqual(Path(str(b) + ".log").read_text(), "seat2 --fail --signal x")
            Path(str(b) + ".full").write_text("")
            self.assertEqual(call("pick")["id"], None)


if __name__ == "__main__":
    unittest.main()
