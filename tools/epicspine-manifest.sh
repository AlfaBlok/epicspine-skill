#!/usr/bin/env bash
# Emit a deterministic sha256 manifest of the EpicSpine skill tree.
#
# Usage: tools/epicspine-manifest.sh [skill-dir]
#
# Output is one "<sha256>  <path>" line per file, sorted by path, suitable for
# committing as MANIFEST.sha256. Consumers vendor this tree and pin the manifest
# so drift becomes visible instead of silent.
set -euo pipefail

dir="${1:-skill/epic-spine}"
cd "$(dirname "$0")/.."

hash_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  else
    shasum -a 256 "$1" | cut -d' ' -f1
  fi
}

export -f hash_file

find "$dir" -type f | LC_ALL=C sort | while IFS= read -r file; do
  printf '%s  %s\n' "$(hash_file "$file")" "$file"
done
