import os
import shutil
from pathlib import Path
from huggingface_hub import hf_hub_download

ROOT = Path("/runpod-volume/models")
# worker-comfyui maps /runpod-volume/models/unet as its diffusion model path.
UNET = ROOT / "unet"
CLIP = ROOT / "clip"
VAE = ROOT / "vae"
for p in (UNET, CLIP, VAE):
    p.mkdir(parents=True, exist_ok=True)

TOKEN = os.getenv("HF_TOKEN") or None
MODELS = [
    (
        "ChrisColeTech/krea2-turbo-uncensored-v1.1-FP8",
        "split/diffusion_models/Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
        UNET / "Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
    ),
    (
        "Comfy-Org/Krea-2",
        "text_encoders/qwen3vl_4b_fp8_scaled.safetensors",
        CLIP / "qwen3vl_4b_fp8_scaled.safetensors",
    ),
    (
        "Comfy-Org/Krea-2",
        "vae/qwen_image_vae.safetensors",
        VAE / "qwen_image_vae.safetensors",
    ),
]

def fetch(repo, filename, dest):
    if dest.exists() and dest.stat().st_size > 1024 * 1024:
        print(f"[Krea2] exists: {dest}", flush=True)
        return
    print(f"[Krea2] downloading {repo}/{filename}", flush=True)
    cached = hf_hub_download(repo_id=repo, filename=filename, token=TOKEN)
    tmp = Path(str(dest) + ".part")
    if tmp.exists():
        tmp.unlink()
    shutil.copy2(cached, tmp)
    tmp.replace(dest)
    print(f"[Krea2] ready: {dest}", flush=True)

for item in MODELS:
    fetch(*item)
print("[Krea2] all models ready", flush=True)
