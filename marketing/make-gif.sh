#!/bin/zsh
# Usage: marketing/make-gif.sh <scene.py> <SceneClass> <name>
# Inspects and renders a ManimGX scene, then converts it to readme-gifs/<name>.gif
# (960x540, high quality, no size cap unless MAX_KB is set). Intermediate MP4s go to .build/marketing/.
set -euo pipefail
cd "$(dirname "$0")/.."

SCENE="${1:?usage: marketing/make-gif.sh <scene.py> <SceneClass> <name>}"
CLASS="${2:?scene class}"
NAME="${3:?gif name}"
MAX_KB="${MAX_KB:-0}"   # 0 = no size limit (user lifted the 2 MB cap)
GIF_FPS="${GIF_FPS:-30}"
OUT_DIR=".build/marketing"
GIF="readme-gifs/$NAME.gif"

command -v ffmpeg >/dev/null || { echo "ffmpeg is required (brew install ffmpeg)."; exit 1; }
if command -v manimgx >/dev/null; then MG=manimgx
else
  [[ -x .venv/bin/manimgx ]] || { python3.14 -m venv .venv && .venv/bin/pip install -q manimgx; }
  MG=.venv/bin/manimgx
fi

mkdir -p "$OUT_DIR"
# Not fatal: faithful UI has small text (caption2, footnote) and overlays (scrim, D-pad backdrop)
# that the checker flags; read its list and the storyboard for real problems.
"$MG" inspect "$SCENE" || echo "inspect: layout notes above (not fatal)"
"$MG" render "$SCENE" "$CLASS" -r 1920x1080 --fps 60
mv "$(dirname "$SCENE")/$CLASS.mp4" "$OUT_DIR/$NAME.mp4"

# Render at 1920x1080/60 and downscale with lanczos; per-frame palette tuned for flat UI colors.
ffmpeg -v error -y -i "$OUT_DIR/$NAME.mp4" -vf \
  "fps=$GIF_FPS,scale=960:540:flags=lanczos,split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
  "$GIF"
SIZE_KB=$(( $(stat -f%z "$GIF") / 1024 ))
echo "$GIF: ${SIZE_KB} KB at ${GIF_FPS} fps, 256 colors"
[[ $MAX_KB -gt 0 && $SIZE_KB -gt $MAX_KB ]] && { echo "over MAX_KB=$MAX_KB"; exit 1; }
exit 0
