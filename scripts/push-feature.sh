#!/bin/zsh
# Pushes the current branch to origin. Refuses main: releases go through release.sh.
set -euo pipefail
cd "$(dirname "$0")/.."

BRANCH=$(git branch --show-current)
if [[ -z "$BRANCH" || "$BRANCH" == "main" ]]; then
  echo "Refusing to push '${BRANCH:-detached HEAD}'. Switch to a feature branch first."
  exit 1
fi
git push -u origin "$BRANCH"
