from __future__ import annotations

import os
import shutil
from pathlib import Path

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

if os.getenv("USE_MOCK_PIPELINE", "0") == "1":
    print("[Krea2 bootstrap] Hub smoke-test mode: skipping model bootstrap.", flush=True)
else:
    from huggingface_hub import hf_hub_download

    volume = Path("/runpod-volume")
    if not volume.exists():
        raise RuntimeError(
            "Krea2 requires a RunPod Network Volume mounted at /runpod-volume."
        )

    root = volume / "models"
    unet = root / "unet"
    clip = root / "clip"
    vae = root / "vae"
    for directory in (unet, clip, vae):
        directory.mkdir(parents=True, exist_ok=True)

    token = os.getenv("HF_TOKEN") or None
    models = [
        (
            "ChrisColeTech/krea2-turbo-uncensored-v1.1-FP8",
            "split/diffusion_models/Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
            unet / "Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
        ),
        (
            "Comfy-Org/Krea-2",
            "text_encoders/qwen3vl_4b_fp8_scaled.safetensors",
            clip / "qwen3vl_4b_fp8_scaled.safetensors",
        ),
        (
            "Comfy-Org/Krea-2",
            "vae/qwen_image_vae.safetensors",
            vae / "qwen_image_vae.safetensors",
        ),
    ]

    def ensure(repo: str, filename: str, dest: Path) -> None:
        # Large model files only; a tiny/partial file is treated as invalid.
        if dest.exists() and dest.stat().st_size > 1024 * 1024:
            print(f"[Krea2 bootstrap] Exists, skip: {dest}", flush=True)
            return

        print(f"[Krea2 bootstrap] Downloading {repo}/{filename}", flush=True)
        cached = hf_hub_download(repo_id=repo, filename=filename, token=token)
        tmp = Path(str(dest) + ".part")
        if tmp.exists():
            tmp.unlink()
        shutil.copy2(cached, tmp)
        tmp.replace(dest)
        print(f"[Krea2 bootstrap] Ready: {dest}", flush=True)

    for model in models:
        ensure(*model)

    print("[Krea2 bootstrap] All models ready.", flush=True)
