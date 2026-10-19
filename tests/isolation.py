"""Hermetic environment for every test: importing this module (once per process) removes the harness config-dir
variables and points HOME at a throwaway dir, so no test, and no subprocess built from ``os.environ``, can read or write
a real ``~/.claude*``, ``CLAUDE_CONFIG_DIR``, ``CODEX_HOME`` or ``XDG_CONFIG_HOME``. ``test_000_isolation.py`` imports it first
under ``discover``; modules that spawn installers import it (via ``fake_bin``) so a single-module run is safe too."""
from __future__ import annotations

import atexit
import os
import shutil
import tempfile

NAMES = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME")
PREFIXES = ("GEMINI_", "EPICSPINE_")  # EPICSPINE_TEST_* are test switches, not config
KEEP = "EPICSPINE_TEST_"


def scrub(environ: dict | None = None) -> dict:
    """Drop config-dir and EpicSpine variables from ``environ`` (default ``os.environ``); returns it."""
    environ = os.environ if environ is None else environ
    for key in list(environ):
        if key in NAMES or (key.startswith(PREFIXES) and not key.startswith(KEEP)):
            del environ[key]
    return environ


def clean_env(**extra: str) -> dict:
    """A copy of the (scrubbed) process env plus ``extra``, for subprocess calls."""
    return {**scrub(dict(os.environ)), **extra}


def _isolate() -> None:
    scrub()
    home = tempfile.mkdtemp(prefix="epicspine-test-home-")
    atexit.register(shutil.rmtree, home, ignore_errors=True)
    os.environ["HOME"] = home


_isolate()
