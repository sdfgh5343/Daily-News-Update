#!/bin/bash

set -e

PROJECT_DIR="$HOME/Daily-News-Update"
CONDA_ENV="$HOME/python-envs/main"

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export FONTCONFIG_PATH="$CONDA_PREFIX/etc/fonts"
export FONTCONFIG_FILE="$CONDA_PREFIX/etc/fonts/fonts.conf"

export DISPLAY=:99

XVFB_STARTED=0

if ! pgrep -f "Xvfb :99" >/dev/null 2>&1; then
    echo "Starting Xvfb..."

    Xvfb :99 \
        -screen 0 1280x720x24 \
        -nolisten tcp \
        > "$HOME/xvfb.log" 2>&1 &

    XVFB_PID=$!
    XVFB_STARTED=1
    sleep 2
fi

cleanup() {
    if [ "$XVFB_STARTED" -eq 1 ]; then
        kill "$XVFB_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT

cd "$PROJECT_DIR"

python crawl.py