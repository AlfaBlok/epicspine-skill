"""Install the pre-commit gate so it runs the ``pre_commit.py`` of the checkout under test (EPIC-4 step 18).

``agents_block.hook_text`` deliberately points an installed hook at the main checkout (``install_guard.install_dir``),
so tests run from a linked worktree would exercise main's gate instead of the branch's. Tests that commit through the
hook install it with ``tree_gate.install`` instead of ``agents_block.install``: the module's own skill dir, worktree or not."""
from __future__ import annotations

from pathlib import Path
from unittest import mock


def install(agents_block, repo: Path, root_spine: str | None = None) -> None:
    with mock.patch.object(agents_block.global_install.ig, "install_dir", lambda skill_dir, *a, **k: skill_dir):
        agents_block.install(repo, root_spine)
