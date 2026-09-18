import os
import shutil
from pathlib import Path
from huggingface_hub import hf_hub_download

VOL = Path("/runpod-volume")
MODEL_ROOT = VOL / "models"
DIFF = MODEL_ROOT / "diffusion_models"
# worker-comfyui extra_model_paths.yaml maps `clip:` to models/clip/.
# CLIPLoader discovers text encoders there as well.
CLIP = MODEL_ROOT / "clip"
VAE = MODEL_ROOT / "vae"

for p in (DIFF, CLIP, VAE):
    p.mkdir(parents=True, exist_ok=True)

token = os.getenv("HF_TOKEN") or None

MODELS = [
    (
        "ChrisColeTech/krea2-turbo-uncensored-v1.1-FP8",
        "split/diffusion_models/Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
        DIFF / "Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
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
        print(f"[Krea2 bootstrap] Exists, skip: {dest}", flush=True)
        return
    print(f"[Krea2 bootstrap] Downloading {repo}/{filename}", flush=True)
    cached = hf_hub_download(repo_id=repo, filename=filename, token=token)
    tmp = dest.with_suffix(dest.suffix + ".part")
    if tmp.exists():
        tmp.unlink()
    shutil.copy2(cached, tmp)
    tmp.replace(dest)
    print(f"[Krea2 bootstrap] Ready: {dest}", flush=True)

for args in MODELS:
    fetch(*args)

print("[Krea2 bootstrap] All models ready.", flush=True)
