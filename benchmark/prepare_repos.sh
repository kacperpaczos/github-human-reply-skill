#!/usr/bin/env bash
# For every built case, put the repository at its state just before the hidden
# reply into benchmark/work/cases/<id>/repo (a git worktree of one partial clone
# per repository). Read-only towards GitHub.
set -euo pipefail
work="$(cd "$(dirname "$0")" && pwd)/work"
mkdir -p "$work/clones"
for h in "$work"/hidden/*.json; do
  id=$(jq -r .id "$h"); repo=$(jq -r .repo "$h"); cut=$(jq -r .cutoff "$h")
  clone="$work/clones/${repo//\//__}"
  dest="$work/cases/$id/repo"
  [ -e "$dest" ] && { echo "have $id"; continue; }
  [ -d "$clone" ] || git clone --quiet --filter=blob:none --no-checkout "https://github.com/$repo.git" "$clone"
  sha=$(git -C "$clone" rev-list -1 --before="$cut" HEAD)
  git -C "$clone" worktree add --quiet --detach "$dest" "$sha"
  echo "ok $id at $sha ($(git -C "$dest" log -1 --format=%cI))"
done
