#!/bin/zsh
# Builds the iPhone app, installs it on a connected physical iPhone and launches it.
# Set DEVICE=<udid> to pick a phone; otherwise the first connected physical one is used.
# The phone must be unlocked, trusted and paired with this Mac.
set -euo pipefail
cd "$(dirname "$0")/.."

BUNDLE_ID="com.altay.lazyremote"
DERIVED=".build/ios"

DEVICE="${DEVICE:-$(xcrun devicectl list devices 2>/dev/null | grep -E 'connected +iPhone|connected.*physical' \
  | grep -oE '[0-9A-F]{8}-[0-9A-F]{16}|[0-9A-F]{8}-([0-9A-F]{4}-){3}[0-9A-F]{12}' | head -1)}"
if [[ -z "$DEVICE" ]]; then
  echo "No connected physical iPhone found. Plug it in, unlock it and tap Trust."
  exit 1
fi
echo "Deploying to device $DEVICE"

xcodegen generate
xcodebuild -project MacRemote.xcodeproj -scheme RemoteDPad -configuration Debug \
  -destination "id=$DEVICE" -derivedDataPath "$DERIVED" -allowProvisioningUpdates -quiet build

APP=$(find "$DERIVED/Build/Products" -maxdepth 2 -name '*.app' -path '*iphoneos*' | head -1)
xcrun devicectl device install app --device "$DEVICE" "$APP"
xcrun devicectl device process launch --device "$DEVICE" --terminate-existing "$BUNDLE_ID"
echo "Installed and launched $BUNDLE_ID. Ready for manual testing."
