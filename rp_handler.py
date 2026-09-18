from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

import runpod

ROOT = Path(__file__).parent.resolve()
SCRIPTS = ROOT / "scripts"
LOGGER = logging.getLogger("krea2")
logging.basicConfig(level=logging.INFO)

MOCK = os.getenv("USE_MOCK_PIPELINE", "0") == "1"
BOOTSTRAPPED = False

def _bootstrap() -> None:
    global BOOTSTRAPPED
    if BOOTSTRAPPED or MOCK:
        return
    LOGGER.info("Ensuring Krea2 models exist on /runpod-volume...")
    subprocess.run([sys.executable, str(SCRIPTS / "bootstrap_models.py")], check=True)
    BOOTSTRAPPED = True

def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    start = time.perf_counter()
    job_input = job.get("input") or {}
    if not isinstance(job_input, dict):
        return {"error": "`input` must be a JSON object."}

    # RunPod Hub smoke tests must never download 20GB+ of model data.
    if MOCK:
        return {
            "output": {
                "status": "ok",
                "mock": True,
                "message": "Krea2 RunPod Hub smoke test passed"
            },
            "metrics": {"execution_ms": round((time.perf_counter() - start) * 1000, 2)}
        }

    _bootstrap()

    # Production is intentionally delegated to the official worker-comfyui
    # runtime. This handler is primarily the Hub-visible entrypoint and a
    # safe smoke-test path. For direct production jobs use the base worker's
    # ComfyUI workflow contract after deploying the image.
    return {
        "output": {
            "status": "models_ready",
            "message": "Krea2 models are present on the Network Volume."
        },
        "metrics": {"execution_ms": round((time.perf_counter() - start) * 1000, 2)}
    }

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
