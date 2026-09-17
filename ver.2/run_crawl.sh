#!/bin/bash

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$HOME/python-envs/main"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export FONTCONFIG_PATH="$CONDA_PREFIX/etc/fonts"
export FONTCONFIG_FILE="$CONDA_PREFIX/etc/fonts/fonts.conf"

if ! pgrep -f "Xvfb :99" >/dev/null; then
    Xvfb :99 \
        -screen 0 1280x720x24 \
        -nolisten tcp \
        > "$HOME/xvfb.log" 2>&1 &
    sleep 2
fi

export DISPLAY=:99

cd "$HOME/Daily-News-Update/ver.2" || exit 1

python crawl.py
