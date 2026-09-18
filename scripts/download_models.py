import os
import shutil
from pathlib import Path
from huggingface_hub import hf_hub_download

COMFY = Path("/comfyui")
DIFF = COMFY / "models" / "diffusion_models"
TEXT = COMFY / "models" / "text_encoders"
VAE = COMFY / "models" / "vae"
for p in (DIFF, TEXT, VAE):
    p.mkdir(parents=True, exist_ok=True)

token = os.getenv("HF_TOKEN") or None

def fetch(repo, filename, dest_dir, dest_name=None):
    print(f"Downloading {repo}/{filename}", flush=True)
    cached = hf_hub_download(
        repo_id=repo,
        filename=filename,
        token=token,
    )
    dest = Path(dest_dir) / (dest_name or Path(filename).name)
    if dest.exists():
        dest.unlink()
    shutil.copy2(cached, dest)
    print(f"Installed -> {dest}", flush=True)

# Krea2 Turbo Edit v1.1 FP8 transformer.
# This exact path is used instead of listing the sensitive repo, because
# repository-list APIs can hide files on Not-For-All-Audiences repos.
fetch(
    "ChrisColeTech/krea2-turbo-uncensored-v1.1-FP8",
    "split/diffusion_models/Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
    DIFF,
    "Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
)

# Public official ComfyUI components.
fetch(
    "Comfy-Org/Krea-2",
    "text_encoders/qwen3vl_4b_fp8_scaled.safetensors",
    TEXT,
)
fetch(
    "Comfy-Org/Krea-2",
    "vae/qwen_image_vae.safetensors",
    VAE,
)

print("All Krea2 models installed.", flush=True)
