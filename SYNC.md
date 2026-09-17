# Keeping EpicSpine in sync

EpicSpine has exactly **one development home**:

- Repository: `https://github.com/AlfaBlok/epicspine-skill`
- Skill path: `skill/epic-spine/`
- Reference commit: whatever is on `main`

Edit the skill **here and only here**. Everything else on disk is a copy.

## Why this file exists

The skill was previously copied into several repositories and, because it is a
git worktree target, into a folder per development branch. Those copies are not
independent projects; they are snapshots. Without a rule, they silently drift and
nobody can tell which version is current. This file is that rule.

## Vocabulary

- **Canonical source** — this repository. The only place the skill is authored.
- **Vendored copy** — a snapshot of `skill/epic-spine/` committed inside another
  repository (for example `zenod/skills/epic-spine/`). It is a copy, not a fork.
  Never edit a vendored copy; re-sync it.
- **Worktree copy** — a checkout of this repository on a development branch. It
  is a scratch space, not distribution. Remove it once the branch is merged.

## Rules

1. Author changes in this repository against `skill/epic-spine/`.
2. Run `tools/epicspine-manifest.sh skill/epic-spine > MANIFEST.sha256` when the
   skill changes, and commit the refreshed manifest with it. CI fails otherwise.
3. Re-sync every vendored copy to the new `main` in one dedicated commit. Record
   the source commit in the consumer (see below).
4. Bind development to a worktree and delete the worktree (and its merged branch)
   once it is merged. Do not let worktrees accumulate.

## Consumer pin

A repository that vendors the skill commits two artefacts next to the copy:

- `<copy>.SOURCE` — the source repo, path, and commit the copy came from.
- `<copy>.manifest.sha256` — the manifest of the vendored tree at that commit.

A check script recomputes the manifest and fails when the working copy no longer
matches the pin. Drift is then a red build, not a mystery.

## Sync procedure

```sh
# 1. Land the change in the canonical source.
cd epicspine-skill
git switch main && git pull --ff-only
tools/epicspine-manifest.sh skill/epic-spine > MANIFEST.sha256
git add skill/epic-spine MANIFEST.sha256 && git commit -m "feat(skill): ..."
# open, review and merge the PR, then note the new main commit

# 2. Re-sync each consumer in its own commit.
CONSUMER=/path/to/consumer
cp -R epicspine-skill/skill/epic-spine/. "$CONSUMER/skills/epic-spine/"
tools/epicspine-manifest.sh "$CONSUMER/skills/epic-spine" > "$CONSUMER/skills/epic-spine.manifest.sha256"
printf 'source: https://github.com/AlfaBlok/epicspine-skill\npath: skill/epic-spine\ncommit: %s\n' \
  "$(git -C epicspine-skill rev-parse main)" > "$CONSUMER/skills/epic-spine.SOURCE"
```

## Drift detection

- Canonical source: CI job **Skill manifest is current** compares
  `MANIFEST.sha256` against a freshly generated manifest.
- Consumers: run the vendored check (`scripts/ci/check-epicspine-vendored.sh` in
  `zenod`) on every push or PR that touches the vendored copy. It fails when the
  copy and its pinned manifest disagree.
