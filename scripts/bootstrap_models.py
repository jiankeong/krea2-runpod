"""Manual model bootstrap helper for a RunPod Pod with the same Network Volume."""
from pathlib import Path
import fcntl
import os
import shutil
from huggingface_hub import hf_hub_download

ROOT = Path("/runpod-volume/models")
CACHE = Path("/runpod-volume/.hf-cache")
LOCK = Path("/runpod-volume/.krea2-model-download.lock")
UNET = ROOT / "unet"   # worker-comfyui maps this to diffusion_models
CLIP = ROOT / "clip"   # worker-comfyui maps this to text_encoders
VAE = ROOT / "vae"
for p in (UNET, CLIP, VAE, CACHE):
    p.mkdir(parents=True, exist_ok=True)

TOKEN = os.getenv("HF_TOKEN") or None
MODELS = [
    ("ChrisColeTech/krea2-turbo-uncensored-v1.1-FP8",
     "split/diffusion_models/Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
     UNET / "Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors"),
    ("Comfy-Org/Krea-2",
     "text_encoders/qwen3vl_4b_fp8_scaled.safetensors",
     CLIP / "qwen3vl_4b_fp8_scaled.safetensors"),
    ("Comfy-Org/Krea-2",
     "vae/qwen_image_vae.safetensors",
     VAE / "qwen_image_vae.safetensors"),
]

LOCK.parent.mkdir(parents=True, exist_ok=True)
with LOCK.open("w") as lock_file:
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
    for repo, filename, dest in MODELS:
        if dest.exists() and dest.stat().st_size > 1024 * 1024:
            print(f"[Krea2] exists: {dest}", flush=True)
            continue
        print(f"[Krea2] downloading: {filename}", flush=True)
        cached = Path(hf_hub_download(repo_id=repo, filename=filename, token=TOKEN, cache_dir=str(CACHE)))
        tmp = Path(str(dest) + ".part")
        if tmp.exists():
            tmp.unlink()
        shutil.copy2(cached, tmp)
        tmp.replace(dest)
        print(f"[Krea2] ready: {dest}", flush=True)

(ROOT / ".krea2-models-ready").write_text("Krea2 Turbo Edit v1.1 FP8 models ready\n")
print("[Krea2] MODEL_DOWNLOAD_COMPLETE", flush=True)
