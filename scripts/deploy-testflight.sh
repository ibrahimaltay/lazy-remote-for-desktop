#!/bin/zsh
# Archives the iPhone app and uploads it to App Store Connect (TestFlight).
# Uses the Apple ID signed in to Xcode (Settings > Accounts); no API key needed.
# Each upload needs a CFBundleVersion (build number) in project.yml that App Store Connect has not seen.
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=".build/testflight"
ARCHIVE="$OUT/LazyRemote.xcarchive"
OPTIONS="$OUT/ExportOptions.plist"
TEAM=$(grep -m1 'DEVELOPMENT_TEAM' project.yml | sed -E 's/.*: *"?([A-Z0-9]+)"?.*/\1/')

rm -rf "$OUT" && mkdir -p "$OUT"
cat > "$OPTIONS" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>method</key><string>app-store-connect</string>
  <key>destination</key><string>upload</string>
  <key>teamID</key><string>$TEAM</string>
  <key>signingStyle</key><string>automatic</string>
</dict></plist>
PLIST

xcodegen generate
xcodebuild -project MacRemote.xcodeproj -scheme RemoteDPad -configuration Release \
  -destination 'generic/platform=iOS' -archivePath "$ARCHIVE" -allowProvisioningUpdates -quiet archive
xcodebuild -exportArchive -archivePath "$ARCHIVE" -exportOptionsPlist "$OPTIONS" \
  -exportPath "$OUT/export" -allowProvisioningUpdates

VERSION=$(grep -m1 'CFBundleShortVersionString' project.yml | sed -E 's/.*"(.*)".*/\1/')
BUILD=$(grep -m1 'CFBundleVersion' project.yml | sed -E 's/.*"(.*)".*/\1/')
echo "Uploaded LazyRemote $VERSION ($BUILD) to App Store Connect. It appears in TestFlight after processing."
