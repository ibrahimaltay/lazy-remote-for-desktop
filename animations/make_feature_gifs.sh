#!/bin/sh
# Render every scene in feature_gifs.py and convert it to a 960x540 looping GIF in feature-gifs/.
set -e
cd "$(dirname "$0")"
mkdir -p feature-gifs
for pair in TrackpadMove:trackpad-move TapClick:tap-click RightClick:right-click Scroll:scroll Drag:drag \
            ThreeFingerSwipe:three-finger-swipe FloatingRemote:floating-remote DPadArrows:dpad-arrows \
            PlayPause:play-pause TypeAndSend:keyboard AnyLanguage:any-language BackspaceEnter:backspace-enter \
            Spotlight:spotlight; do
  scene=${pair%%:*}; name=${pair#*:}
  .venv/bin/manimgx render feature_gifs.py "$scene" --fps 25 >/dev/null
  ffmpeg -loglevel error -y -i "$scene.mp4" -vf \
    "scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a" \
    -loop 0 "feature-gifs/$name.gif"
  rm "$scene.mp4"
  echo "feature-gifs/$name.gif"
done
