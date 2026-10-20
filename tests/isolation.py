"""Hermetic environment for every test: importing this module (once per process) redirects HOME, ``CLAUDE_CONFIG_DIR``,
``CODEX_HOME`` and ``XDG_CONFIG_HOME`` to fresh temp dirs and drops ``GEMINI_*`` and ``EPICSPINE_*`` variables (except
``EPICSPINE_TEST_*`` switches), so no test, and no subprocess built from ``os.environ``, can read or write a real
``~/.claude*``, ``~/.codex`` or ``~/.config``. ``test_000_isolation.py`` imports it first under ``discover`` (modules load
in sorted order); ``_safe_env`` and ``fake_bin`` import it so a single-module run is safe too."""
from __future__ import annotations

import atexit
import os
import shutil
import tempfile

ORIGINAL = {k: os.environ.get(k) for k in ("HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME", "XDG_CONFIG_HOME")}
NAMES = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "XDG_CONFIG_HOME")
DROP_PREFIXES = ("GEMINI_", "EPICSPINE_")
KEEP = "EPICSPINE_TEST_"


def drop(environ: dict | None = None) -> dict:
    """Remove GEMINI_* and EPICSPINE_* (not EPICSPINE_TEST_*) from ``environ`` (default ``os.environ``); returns it."""
    environ = os.environ if environ is None else environ
    for key in list(environ):
        if key.startswith(DROP_PREFIXES) and not key.startswith(KEEP):
            del environ[key]
    return environ


def _isolate() -> None:
    drop()
    home = tempfile.mkdtemp(prefix="epicspine-test-home-")
    atexit.register(shutil.rmtree, home, ignore_errors=True)
    os.environ["HOME"] = home
    for name in NAMES:
        path = os.path.join(home, "." + name.lower())
        os.makedirs(path)
        os.environ[name] = path


_isolate()
