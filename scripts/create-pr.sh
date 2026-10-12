#!/bin/zsh
# Opens a PR from the current feature branch into main, filled from its commits.
# Refuses main, and prints the URL instead if the branch already has an open PR (merged ones don't count).
set -euo pipefail
cd "$(dirname "$0")/.."

BRANCH=$(git branch --show-current)
if [[ -z "$BRANCH" || "$BRANCH" == "main" ]]; then
  echo "Refusing to open a PR from '${BRANCH:-detached HEAD}'. Switch to a feature branch first."
  exit 1
fi
if [[ -n "$(git status --porcelain)" || -n "$(git log '@{u}..' --oneline 2>/dev/null)" ]]; then
  echo "Uncommitted or unpushed work on $BRANCH. Commit and run push-feature.sh first."
  exit 1
fi
EXISTING=$(gh pr list --head "$BRANCH" --state open --json url -q '.[0].url')
if [[ -n "$EXISTING" ]]; then
  echo "$EXISTING"
  exit 0
fi
gh pr create --base main --head "$BRANCH" --fill
