from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("t3_seat_pool_t", ROOT / "examples/dispatchers/t3_seat_pool.py")
adapter = importlib.util.module_from_spec(spec)
sys.modules["t3_seat_pool_t"] = adapter
spec.loader.exec_module(adapter)


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
