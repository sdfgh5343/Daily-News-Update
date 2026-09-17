#!/bin/bash

set -euo pipefail

PROJECT_DIR="$HOME/Daily-News-Update"
CONDA_ENV="$HOME/python-envs/main"

echo "===== 1. Activate Conda ====="

source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

echo "[OK] Conda"

echo "===== 2. Run Liner.py ====="

cd "$PROJECT_DIR"

python Liner.py

echo "[OK] Liner.py"

echo "======================================"
echo " LINE MESSAGE COMPLETED SUCCESSFULLY"
echo "======================================"
