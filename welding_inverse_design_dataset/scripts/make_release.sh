#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

python3 -m pip install -r "$ROOT_DIR/requirements.txt"
python3 "$ROOT_DIR/scripts/generate.py" --n 20000 --seed 1337 --out "$ROOT_DIR"

cd "$ROOT_DIR"
zip -r "dataset_release.zip" data/ docs/ requirements.txt pyproject.toml

echo "Release archive at $ROOT_DIR/dataset_release.zip"
