#!/usr/bin/env bash
# One-command build: SFX -> frames -> MP4 (+ cover).  Usage: bash tools/build.sh
# First run creates .venv/ here (numpy + imageio-ffmpeg, which ships its own ffmpeg).
# Optional overrides: PYTHON, FFMPEG, CHROME_EXE, PW_CORE, WORKERS.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -z "${PYTHON:-}" ]; then
  PYTHON=.venv/bin/python
  if ! "$PYTHON" -c 'import numpy, imageio_ffmpeg' 2>/dev/null; then
    echo "setting up .venv (numpy, imageio-ffmpeg) ..."
    python3 -m venv .venv
    "$PYTHON" -m pip install -q -r requirements.txt
  fi
fi
if [ -z "${FFMPEG:-}" ]; then
  if command -v ffmpeg >/dev/null 2>&1; then
    FFMPEG=ffmpeg
  else
    FFMPEG=$("$PYTHON" -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')
  fi
fi

"$PYTHON" tools/audio.py build/sfx.wav
rm -rf build/frames
node tools/render.mjs --all --workers "${WORKERS:-7}"

mkdir -p out
"$FFMPEG" -hide_banner -loglevel error -y \
  -framerate 30 -i build/frames/f_%05d.png -i build/sfx.wav \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -r 30 \
  -c:a aac -b:a 192k -ar 48000 \
  -t 75 -movflags +faststart \
  out/边听歌边背书_75s_1080p.mp4
cp build/frames/f_00000.png out/第0帧.png
node tools/render.mjs --covers
echo "built out/边听歌边背书_75s_1080p.mp4"
