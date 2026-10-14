#!/bin/zsh
# Builds the signed, notarized DMG (see release-mac.sh) and installs it on this Mac for manual QA.
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/release-mac.sh
./scripts/install-mac.sh
