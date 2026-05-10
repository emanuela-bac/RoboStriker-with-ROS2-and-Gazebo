#!/usr/bin/env bash
# Simple demo capture script for RoboStriker
# Usage: ./scripts/capture_demo.sh <out.gif> <duration_seconds> [<crop_x:crop_y:widthxheight>]
# Example: ./scripts/capture_demo.sh /tmp/demo.gif 8 100:100:800x600

set -euo pipefail
OUT=${1:-/tmp/robo_demo.gif}
DURATION=${2:-8}
CROP=${3:-}
TMP_DIR=$(mktemp -d)
RAW_MP4="$TMP_DIR/raw_capture.mp4"
PALETTE="$TMP_DIR/palette.png"

# Detect display environment
if [ -z "${DISPLAY:-}" ]; then
  echo "DISPLAY not set. This script uses X11 screen capture (ffmpeg)."
  echo "If you are on Wayland, run an XWayland session or use OBS/other recorder." >&2
fi

# Build crop option for ffmpeg if provided
CROP_OPT=""
if [ -n "$CROP" ]; then
  # Expect format X:Y:WxH
  # ffmpeg expects: -filter:v "crop=W:H:X:Y"
  IFS=':' read -r CX CY WH <<< "$CROP"
  W=${WH%x*}
  H=${WH#*x}
  CROP_OPT="-filter:v crop=${W}:${H}:${CX}:${CY}"
fi

# Record the screen to MP4 (x11grab). Adjust framerate 15 for small GIFs.
echo "Recording screen for ${DURATION}s -> ${RAW_MP4}"
ffmpeg -y -video_size 1920x1080 -framerate 15 -f x11grab -i "$DISPLAY" -t "$DURATION" $CROP_OPT -c:v libx264 -pix_fmt yuv420p -preset ultrafast "$RAW_MP4"

# Make palette and create gif (optimized)
ffmpeg -y -i "$RAW_MP4" -vf "palettegen" -y "$PALETTE"
ffmpeg -y -i "$RAW_MP4" -i "$PALETTE" -lavfi "paletteuse" -r 15 "$OUT"

# Optional: further optimize with gifsicle if available
if command -v gifsicle >/dev/null 2>&1; then
  echo "Optimizing GIF with gifsicle"
  gifsicle -O3 --colors 256 "$OUT" -o "$OUT"
fi

echo "GIF written to: $OUT"
rm -rf "$TMP_DIR"
exit 0
