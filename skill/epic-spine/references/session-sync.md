# Session self-sync

`scripts/session_sync.py` runs from the SessionStart hook, so no agent has to remember to upgrade (`EPICSPINE_SYNC=off` disables it; one 10 s deadline, short per-call timeouts, never raises, never forces):

- **Skill**, at most once per 10 minutes (stamp `~/.agents/epicspine-sync.stamp`): a source checkout (skill dir is `<repo>/skill/epic-spine`) is fetched and fast-forwarded when its tree is clean and only behind; a pinned or unpinned installed copy uses `skill_update.py`'s verified upgrade when `ls-remote` shows a new commit. Vendored copies are left to `SYNC.md`; a repo `Skill updates: off|manual` skips it. Context line: `EpicSpine sync: skill 2026.10.16.3 -> 2026.10.16.4`.
- **Profile**: `~/.agents/epicspine-profile.md` is rewritten from `assets/epicspine-profile.md` unless `~/.agents/epicspine-profile.local.md` exists (`agents_block.py profile --set` writes that override).
- **Repo** (`scripts/repo_sync.py`): fetch; clean + only behind -> fast-forward; ahead on the integration branch -> push fast-forward-only (not under `Integration policy: pr-approval`); diverged, or behind with a dirty tree, on the integration branch -> nothing changes and an `EpicSpine attention:` line names the repo and why.
- **Repo setup**: a repo with a discoverable root spine but no current AGENTS.md block gets `agents_block.py install`, and a root spine lacking `## Operating Learnings` gets an empty section; left uncommitted, one `EpicSpine setup:` line asks the agent to commit. No spine: nothing is written.

New machine, one line: `git clone https://github.com/AlfaBlok/epicspine-skill ~/github/epicspine-skill && python3 ~/github/epicspine-skill/skill/epic-spine/scripts/agents_block.py install-global`.

