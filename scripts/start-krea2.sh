#!/usr/bin/env bash
set -euo pipefail

echo "[Krea2] Checking persistent models in /runpod-volume..."
python /opt/krea2/bootstrap_models.py

echo "[Krea2] Starting official worker-comfyui..."
# The base image currently starts through /start.sh.
exec /start.sh
