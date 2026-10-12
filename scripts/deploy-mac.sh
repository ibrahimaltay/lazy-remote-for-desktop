#!/bin/zsh
# Builds the signed, notarized DMG (see release-mac.sh) and reveals it in Finder for manual QA.
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/release-mac.sh
open -R .build/release/LazyRemote.dmg
