from __future__ import annotations
import os
import shutil
import threading
from pathlib import Path

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def bootstrap():
    try:
        from huggingface_hub import hf_hub_download

        # Prefer Network Volume. Never crash ComfyUI if it is not mounted.
        volume = Path("/runpod-volume")
        if volume.exists() and os.access(volume, os.W_OK):
            root = volume / "models"
            print("[Krea2 bootstrap] Using Network Volume: /runpod-volume", flush=True)
        else:
            root = Path("/comfyui/models")
            print("[Krea2 bootstrap] WARNING: /runpod-volume is unavailable; "
                  "using ephemeral /comfyui/models.", flush=True)

        unet, clip, vae = root/"unet", root/"clip", root/"vae"
        for p in (unet, clip, vae):
            p.mkdir(parents=True, exist_ok=True)

        token = os.getenv("HF_TOKEN") or None
        models = [
            ("ChrisColeTech/krea2-turbo-uncensored-v1.1-FP8",
             "split/diffusion_models/Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
             unet/"Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors"),
            ("Comfy-Org/Krea-2",
             "text_encoders/qwen3vl_4b_fp8_scaled.safetensors",
             clip/"qwen3vl_4b_fp8_scaled.safetensors"),
            ("Comfy-Org/Krea-2",
             "vae/qwen_image_vae.safetensors",
             vae/"qwen_image_vae.safetensors"),
        ]

        for repo, filename, dest in models:
            if dest.exists() and dest.stat().st_size > 1024 * 1024:
                print(f"[Krea2 bootstrap] Exists: {dest}", flush=True)
                continue
            print(f"[Krea2 bootstrap] Downloading: {filename}", flush=True)
            cached = hf_hub_download(repo_id=repo, filename=filename, token=token)
            tmp = Path(str(dest) + ".part")
            if tmp.exists():
                tmp.unlink()
            shutil.copy2(cached, tmp)
            tmp.replace(dest)
            print(f"[Krea2 bootstrap] Ready: {dest}", flush=True)

        print("[Krea2 bootstrap] MODEL_DOWNLOAD_COMPLETE", flush=True)
    except Exception as exc:
        # Critical: custom-node import must never terminate ComfyUI.
        print(f"[Krea2 bootstrap] ERROR (non-fatal): {type(exc).__name__}: {exc}", flush=True)

if os.getenv("USE_MOCK_PIPELINE", "0") == "1":
    print("[Krea2 bootstrap] Hub test mode; download skipped.", flush=True)
else:
    # Do not block ComfyUI readiness while downloading multi-GB weights.
    threading.Thread(target=bootstrap, name="krea2-bootstrap", daemon=True).start()
