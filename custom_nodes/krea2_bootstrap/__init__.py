from __future__ import annotations

import os

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# IMPORTANT: RunPod Hub smoke tests must take the exact lightweight path.
# Do not import/download/lock/touch Network Volume in test mode.
if os.getenv("USE_MOCK_PIPELINE", "0") == "1":
    print("[Krea2 bootstrap] Hub test mode; bootstrap completely skipped.", flush=True)
else:
    import threading

    def bootstrap():
        try:
            # Production-only imports. Hub tests never execute/import these.
            import fcntl
            import shutil
            from pathlib import Path
            from huggingface_hub import hf_hub_download

            min_valid_bytes = 1024 * 1024

            def valid(path: Path) -> bool:
                return path.exists() and path.stat().st_size > min_valid_bytes

            volume = Path("/runpod-volume")
            if volume.exists() and os.access(volume, os.W_OK):
                root = volume / "models"
                cache_dir = volume / ".hf-cache"
                lock_path = volume / ".krea2-model-download.lock"
                print("[Krea2 bootstrap] Using Network Volume: /runpod-volume", flush=True)
            else:
                root = Path("/comfyui/models")
                cache_dir = Path("/tmp/krea2-hf-cache")
                lock_path = Path("/tmp/.krea2-model-download.lock")
                print(
                    "[Krea2 bootstrap] WARNING: /runpod-volume is unavailable; "
                    "using ephemeral /comfyui/models.",
                    flush=True,
                )

            # worker-comfyui maps unet -> diffusion_models and clip -> text_encoders.
            unet = root / "unet"
            clip = root / "clip"
            vae = root / "vae"
            for path in (unet, clip, vae, cache_dir):
                path.mkdir(parents=True, exist_ok=True)

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

            lock_path.parent.mkdir(parents=True, exist_ok=True)
            with lock_path.open("w") as lock_file:
                print("[Krea2 bootstrap] Waiting for model download lock...", flush=True)
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                print("[Krea2 bootstrap] Model download lock acquired.", flush=True)

                # Another worker may have completed the download while we waited.
                for repo, filename, dest in models:
                    if valid(dest):
                        print(f"[Krea2 bootstrap] Exists: {dest}", flush=True)
                        continue

                    print(f"[Krea2 bootstrap] Downloading: {filename}", flush=True)
                    cached = Path(
                        hf_hub_download(
                            repo_id=repo,
                            filename=filename,
                            token=token,
                            cache_dir=str(cache_dir),
                        )
                    )
                    tmp = Path(str(dest) + ".part")
                    if tmp.exists():
                        tmp.unlink()
                    shutil.copy2(cached, tmp)
                    tmp.replace(dest)
                    print(f"[Krea2 bootstrap] Ready: {dest}", flush=True)

                (root / ".krea2-models-ready").write_text(
                    "Krea2 Turbo Edit v1.1 FP8 models ready\n", encoding="utf-8"
                )
                print("[Krea2 bootstrap] MODEL_DOWNLOAD_COMPLETE", flush=True)

        except Exception as exc:
            # Never terminate ComfyUI because model bootstrap failed.
            print(
                f"[Krea2 bootstrap] ERROR (non-fatal): {type(exc).__name__}: {exc}",
                flush=True,
            )

    # Production bootstrap remains non-blocking so worker-comfyui can become ready.
    threading.Thread(target=bootstrap, name="krea2-bootstrap", daemon=True).start()
