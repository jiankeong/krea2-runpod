#!/usr/bin/env bash
set -euo pipefail

if [[ "${USE_MOCK_PIPELINE:-0}" == "1" ]]; then
  echo "[Krea2] Hub smoke-test mode: skip model bootstrap."
  exec /start.sh
fi

echo "[Krea2] Production mode: checking models on /runpod-volume..."
python /workspace/scripts/bootstrap_models.py

echo "[Krea2] Models ready. Starting official worker-comfyui runtime..."
exec /start.sh
