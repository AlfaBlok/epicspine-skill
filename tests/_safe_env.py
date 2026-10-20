"""``safe_env(**overrides)``: a subprocess env copy of ``os.environ`` that can never carry a real config dir."""
from __future__ import annotations

import os

import isolation

CONFIG_VARS = isolation.NAMES


def safe_env(**overrides: str) -> dict:
    """``os.environ`` copy with config-dir vars, GEMINI_* and EPICSPINE_* (not EPICSPINE_TEST_*) removed; then
    ``overrides`` applied (an explicit ``CLAUDE_CONFIG_DIR=`` etc. is honored)."""
    env = isolation.drop(dict(os.environ))
    for name in CONFIG_VARS:
        env.pop(name, None)
    env.update(overrides)
    return env
