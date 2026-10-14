#!/bin/zsh
# Installs .build/release/LazyRemote.dmg into /Applications, relaunches it and verifies the binary hash.
set -euo pipefail
cd "$(dirname "$0")/.."

DMG=".build/release/LazyRemote.dmg"
DEST="/Applications/LazyRemote.app"
[[ -f "$DMG" ]] || { echo "Missing $DMG; run scripts/deploy-mac.sh"; exit 1; }

MNT=$(mktemp -d)
cleanup() { hdiutil detach "$MNT" -quiet 2>/dev/null || true; rmdir "$MNT" 2>/dev/null || true; }
trap cleanup EXIT

hdiutil attach "$DMG" -readonly -nobrowse -mountpoint "$MNT" -quiet
SRC="$MNT/LazyRemote.app"
[[ -d "$SRC" ]] || { echo "LazyRemote.app not found in DMG"; exit 1; }

if pgrep -x LazyRemote >/dev/null; then
  osascript -e 'tell application "LazyRemote" to quit' || true
  for _ in {1..20}; do pgrep -x LazyRemote >/dev/null || break; sleep 0.5; done
  pkill -x LazyRemote 2>/dev/null || true
  sleep 1
fi

rm -rf "$DEST"
ditto "$SRC" "$DEST"

EXE=$(defaults read "$DEST/Contents/Info" CFBundleExecutable)
SRC_SUM=$(shasum "$SRC/Contents/MacOS/$EXE" | cut -d' ' -f1)
DST_SUM=$(shasum "$DEST/Contents/MacOS/$EXE" | cut -d' ' -f1)
if [[ "$SRC_SUM" != "$DST_SUM" ]]; then
  echo "HASH MISMATCH: DMG $SRC_SUM vs installed $DST_SUM"
  exit 1
fi

open "$DEST"
echo "Installed $(defaults read "$DEST/Contents/Info" CFBundleShortVersionString) (build $(defaults read "$DEST/Contents/Info" CFBundleVersion)), sha $DST_SUM matches DMG"
