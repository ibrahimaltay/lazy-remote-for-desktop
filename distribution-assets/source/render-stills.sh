#!/bin/zsh
# Renders 4K stills of the four scenes into distribution-assets/source/frames/ (needs .venv with manimgx).
cd "$(dirname "$0")/../.."
export LAZYREMOTE_DEVICE_NAME="My Computer"   # no Apple device names in store art
mkdir -p distribution-assets/source/frames .build
for c in StillRemote StillKeyboard StillSpotlight StillTrackpad; do
  .venv/bin/manimgx render distribution-assets/source/stills.py $c -r 3840x2160 --fps 5 >/dev/null 2>&1   # exits non-zero on layout notes
  mv distribution-assets/source/$c.mp4 .build/$c.mp4
  ffmpeg -v error -y -i .build/$c.mp4 -frames:v 1 -update 1 distribution-assets/source/frames/$c.png
done
rm -f distribution-assets/source/*.storyboard.png
