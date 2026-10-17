#!/usr/bin/env bash
# One-shot environment for the video engine inside a Kiro sandbox (Amazon Linux 2023, no root writes).
#
#   bash .kiro/skills/vibe-knowledge-video/scripts/setup_env.sh [ENV_DIR]
#
# Creates ENV_DIR (default /projects/sandbox/.videoenv) with a venv and a wrapper:
#   $ENV_DIR/vpy  ->  python with LD_LIBRARY_PATH set for skia (libEGL/libGL)
# Notes from experience:
#   * pip --user fails (read-only ~/.local) -> use a venv under /projects/sandbox
#   * /tmp is not shared between tool calls -> keep everything under /projects/sandbox
#   * skia-python needs libEGL.so.1 + libGL.so.1, not installed and dnf can't write /var
#     -> dnf --downloadonly into a local dir, unpack the rpms with cpio_extract.py
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="${1:-/projects/sandbox/.videoenv}"
mkdir -p "$ENV_DIR"
PY="$ENV_DIR/venv/bin/python"
GL="$ENV_DIR/gl/usr/lib64"

[ -x "$PY" ] || python3 -m venv "$ENV_DIR/venv"
"$PY" -m pip install -q --disable-pip-version-check numpy scipy soundfile skia-python imageio-ffmpeg librosa

cat > "$ENV_DIR/vpy" <<EOF
#!/usr/bin/env bash
export LD_LIBRARY_PATH="$GL:\${LD_LIBRARY_PATH:-}"
exec "$PY" "\$@"
EOF
chmod +x "$ENV_DIR/vpy"

if ! "$ENV_DIR/vpy" -c "import skia" 2>/dev/null; then
  echo "skia needs libEGL/libGL -> downloading mesa rpms locally"
  W="$ENV_DIR/dnf"
  mkdir -p "$W/rpms" "$W/log" "$W/cache" "$W/persist"
  dnf install -y -q --downloadonly --destdir="$W/rpms" \
      --setopt=logdir="$W/log" --setopt=cachedir="$W/cache" --setopt=persistdir="$W/persist" \
      mesa-libEGL mesa-libGL libglvnd-egl libglvnd-glx libglvnd-opengl
  for f in "$W"/rpms/*.rpm; do rpm2cpio "$f" | python3 "$HERE/cpio_extract.py" "$ENV_DIR/gl"; done
fi

"$ENV_DIR/vpy" -c "import skia, imageio_ffmpeg, librosa, soundfile, scipy; skia.Surface(8, 8); print('OK  skia', skia.__version__, '| ffmpeg', imageio_ffmpeg.get_ffmpeg_exe())"
echo "Use: $ENV_DIR/vpy <script.py>   (run from the repo root for 'python -m engine.xxx')"
