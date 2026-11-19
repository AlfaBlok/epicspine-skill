"""The owner's numbers over a pack's check params (agent_team E46-S93: he sets posts a day from his console's Settings).

A JSON file named by EPICSPINE_PACK_PARAMS, else ~/.config/epicspine/pack-params.json, shaped
`{"params": {"<pack>": {"<check>": {"<param>": value}}}}`, lies over `checks.<check>.params` of each loaded pack; a map
param merges key by key. No file (or no entry): the pack's own numbers.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def owner_params() -> dict:
    raw = os.environ.get("EPICSPINE_PACK_PARAMS") or str(Path.home() / ".config" / "epicspine" / "pack-params.json")
    try:
        return json.loads(Path(raw).read_text(encoding="utf-8")).get("params") or {}
    except (OSError, ValueError, AttributeError):
        return {}


def lay_over(name: str, schema: dict) -> dict:
    for check, over in (owner_params().get(name) or {}).items():
        params = schema.get("checks", {}).get(check, {}).get("params")
        if not isinstance(params, dict) or not isinstance(over, dict):
            continue
        for k, v in over.items():
            params[k] = {**params[k], **v} if isinstance(v, dict) and isinstance(params.get(k), dict) else v
    return schema
