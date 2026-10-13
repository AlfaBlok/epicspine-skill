# Guards

Read this when a hook blocks you, or when installing, configuring, or debugging the enforcement hooks. Written rules drift; the rules below are enforced by Claude Code hooks that `agents_block.py install-global` registers (`--no-hooks` skips, `uninstall-global` removes only ours).

| Hook | Event | Enforces |
|---|---|---|
| `scripts/manager_guard.py` | `PreToolUse` (`Bash\|Edit\|Write\|MultiEdit\|NotebookEdit\|mcp__.*`) | The manager never implements |
| `scripts/push_gate.py` | `Stop` | Every session ends with work committed and pushed to the shared remote |
| `scripts/url_gate.py` | `Stop` | HTML/visual deliverables as served URLs (`artifacts.md`) |

Codex, Gemini CLI and the others get the instruction block only; no verified tool-call hook exists there.

## Manager Or Worker

The guard applies to the manager only. In order:

1. A tool call made inside a subagent carries `agent_id` (and `agent_type`) in the hook input; the main thread's calls do not. Verified on Claude Code 2.1.296 with a logging hook: main-thread `Bash` had neither field, the subagent's `Bash` had both. Subagent → worker, always allowed. High confidence; it is the harness's own field.
2. `EPICSPINE_ROLE=worker|manager` in the session's environment decides next (set it when launching a worker session by hand, or to force the guard on in a worktree).
3. A session whose project dir (`CLAUDE_PROJECT_DIR`, else `cwd`) is a linked git worktree is a worker: top-level worker sessions (T3 threads, `claude -p` in `../wt-x`, `.claude/worktrees/*`) run there. The project dir, not the shell's current directory, is used, so a manager cannot `cd` into a worktree to escape. Medium confidence: a manager deliberately started inside a worktree is treated as a worker; use `EPICSPINE_ROLE=manager` there.
4. Anything else inside a git repo is the manager. Outside a git repo the guard does nothing.

## What The Manager May Do

Allowlist-first: every simple command in a Bash line (split on `;`, `&&`, `||`, `|`, `&`, newlines; `$(...)`, backticks, `bash -c`, `find -exec`, `xargs` and ssh remote commands are checked too) must be recognised, or the call is denied.

| Allowed | Denied (dispatch a worker) |
|---|---|
| Reads: `cat grep rg ls find sed -n awk jq wc diff ps lsof`, … | `sed -i`, `find -delete`, writes via `>`/`tee`/`cp`/`mv`/`rm`/`touch` into the repo |
| `git status log diff show fetch branch -d remote -v worktree list/add/remove` | `git commit` of non-spine files, `clone`, `init`, `reset`, `restore`, `clean`, `stash`, `cherry-pick`, `checkout -b`, `branch -D`, `merge` without `--ff-only` |
| Integrate: `git -C <worktree> rebase main`, `git merge --ff-only`, `git pull --ff-only`, `git push` (no force/delete), `git revert`, `git checkout main` | `git rebase` in the main checkout, `push --force`/`+ref`/`:ref`, `worktree remove --force` |
| Spines: Edit/Write/commit `docs/spines/**` and any `.md` with a `Spine ID:` header; memory (`~/.claude*/projects/*/memory/`, `~/.claude*/plans/`), `~/.agents/epicspine-profile.md`; scratch files outside any repo | Edit/Write/NotebookEdit of code, README, config, AGENTS.md |
| `gh … view/list/status/diff/checks`, `gh api` GET, `gh issue create/comment/edit/close`, `gh pr comment` | `gh repo create/edit/delete/clone`, `gh pr create/merge`, `gh release create`, `gh workflow run`, `gh api` with a write method or fields |
| Tests: `python3 -m unittest`, `pytest`, `npm test`, `cargo test`, `go test`, `make test` | Package installs (`npm i`, `pip install`, `brew install`), builds, `node script.js`, `bash deploy.sh` |
| EpicSpine scripts (`validate_spine.py`, `rollup_spine.py`, `agents_block.py`, `skill_update.py`), `python3 -c` that only reads | `python3 -c`/heredoc code using `subprocess`, `os.remove`, `open(…,'w')`, … |
| `python3 -m http.server --bind 127.0.0.1`, `kill <pid>`, `pkill -f http.server`, `curl` GET, `open http://…` | `http.server` without `--bind 127.0.0.1`, `curl -X POST/-d/-F/-O`, `wget` |
| `ssh host '<read-only command>'` (the remote command passes the same read-only policy) | Interactive `ssh host`, `ssh` with a write command, `scp`, `rsync`, `sftp` |
| Dispatch: Agent tool, `claude -p`, `codex exec`, T3 `delegate_task` / `t3_thread_launch`, `$EPICSPINE_DISPATCHER status\|pick\|done` (or its literal env value) | `sudo`, `eval`, `systemctl restart`, `launchctl load`, `docker run`, `kubectl apply`, T3 `t3_project_create/clone/delete/update`, filesystem/GitHub MCP write tools |

## Per-Repo Configuration

Lines anywhere in the repo's `AGENTS.md` (outside the managed block):

- `Manager guard: enforce` (default) | `warn` (allow, but show the message) | `off`.
- `Manager may edit: MANIFEST.sha256, docs/status/*.md` — extra globs, relative to the repo root.
- ``Manager may run: `tools/epicspine-manifest.sh`, `make status` `` — extra command prefixes (backticks or commas).
- `Push on close: enforce` (default) | `warn` | `off`.

## Escape Hatch

The user, not the agent, grants a one-off: `touch ~/.agents/epicspine-allow` lets the next denied action through (`echo 5 > ~/.agents/epicspine-allow` lets five); it expires after 30 minutes. Any tool call that mentions the marker is denied, so the manager cannot grant itself one. `EPICSPINE_MANAGER_GUARD=off` disables the guard for a session. Every deny, warn and override is appended to `~/.agents/epicspine-guard.log`. When denied after the user explicitly asked you to do the work yourself, ask the user to create the marker; never work around the guard.

## Push On Close

`push_gate.py` runs when a final answer is produced (the `Stop` event; Claude Code's `SessionEnd` cannot block or reach the model). It checks the session's repo:

- Manager: uncommitted files (tracked changes and untracked files), commits not on the upstream (or, without an upstream, on no remote branch), and EpicSpine worker worktrees (`.claude/worktrees/*` or branch `wt/*`) with uncommitted or unintegrated commits.
- Worker (linked worktree): uncommitted files; unpushed commits only when the branch has an upstream (otherwise the manager integrates and pushes).
- A repo with no remote is noted to the user, never blocked.

It blocks with `N uncommitted files, M unpushed commits on <branch> — commit and push (or say why not) before closing.` once per distinct state per session: explaining why not ends the loop, and an unchanged dirty repo does not nag every turn. It stays quiet while background subagents are still running. `EPICSPINE_PUSH_GATE=off` disables it. The manager commits and pushes spine changes itself; non-spine leftovers go to a worker.

## Known False Positives

- A manager deliberately running in a worktree is a worker unless `EPICSPINE_ROLE=manager` is set.
- Unrecognised read-only tools (for example a project CLI's `status` command) are denied until listed under `Manager may run:`.
- `python3 -c` that merely mentions `os.` write helpers, `subprocess` or `open(…, 'w')` is denied even if it never runs them.
- Generating artefacts in the main checkout (manifest refresh, lockfile) needs `Manager may edit:` + `Manager may run:` lines.
- `git add .`/`-A` is denied when anything non-spine is dirty, even if only the spine was meant.
- Both hooks fail open on internal errors, so a broken install never bricks a session; check the log.
