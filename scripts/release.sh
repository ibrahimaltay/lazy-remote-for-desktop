#!/bin/zsh
# Usage: scripts/release.sh <tag> <mac|iphone|both>
#   e.g. v1.6.0 mac    v1.6.0-beta.1 both    v1.6.0 iphone
# A '-' in the tag makes it a pre-release.
# mac/both attach the DMGs built by release-mac.sh and become the "latest" release, which the
# website's download link relies on. iphone-only releases carry notes only and never become "latest",
# so the DMG link keeps pointing at the last Mac build.
# Needs: gh (authenticated), a clean tree, hand-written notes in docs/releases/<tag>.md.
set -euo pipefail
cd "$(dirname "$0")/.."

TAG="${1:?usage: scripts/release.sh <tag> <mac|iphone|both>}"
WHAT="${2:?usage: scripts/release.sh <tag> <mac|iphone|both>}"
NOTES="docs/releases/$TAG.md"
OUT=".build/release"
# Both apps share one version in project.yml, so the first match is enough.
VERSION=$(grep 'CFBundleShortVersionString' project.yml | head -1 | sed -E 's/.*"(.*)".*/\1/')

[[ "$WHAT" == (mac|iphone|both) ]] || { echo "Second argument must be mac, iphone or both."; exit 1; }
command -v gh >/dev/null || { echo "gh is not installed (brew install gh) or not logged in (gh auth login)."; exit 1; }
[[ -f "$NOTES" ]] || { echo "Missing release notes: $NOTES"; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo "Working tree is not clean."; exit 1; }

FLAGS=() ASSETS=()
[[ "$TAG" == *-* ]] && FLAGS+=(--prerelease)
if [[ "$WHAT" == iphone ]]; then
  FLAGS+=(--latest=false)
else
  [[ -f "$OUT/LazyRemote.dmg" && -f "$OUT/LazyRemote-$VERSION.dmg" ]] || { echo "Build the DMG first: scripts/release-mac.sh"; exit 1; }
  ASSETS=("$OUT/LazyRemote.dmg" "$OUT/LazyRemote-$VERSION.dmg")
fi

git tag "$TAG"
git push origin "$TAG"
gh release create "$TAG" "${FLAGS[@]}" --title "$TAG" --notes-file "$NOTES" "${ASSETS[@]}"
