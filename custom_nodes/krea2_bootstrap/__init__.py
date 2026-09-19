from __future__ import annotations

import os

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Hub smoke tests must never touch Hugging Face or the Network Volume.
if os.getenv("USE_MOCK_PIPELINE", "0") == "1":
    print("[Krea2 bootstrap] Hub test mode; bootstrap completely skipped.", flush=True)
else:
    # v5.8.2 intentionally runs SYNCHRONOUSLY during ComfyUI custom-node import.
    # This guarantees the model files exist before ComfyUI accepts API jobs.
    try:
        import fcntl
        import shutil
        from pathlib import Path
        from huggingface_hub import hf_hub_download

        MIN_VALID_BYTES = 1024 * 1024

        volume = Path("/runpod-volume")
        if not (volume.exists() and os.access(volume, os.W_OK)):
            raise RuntimeError(
                "/runpod-volume is not mounted or writable. "
                "Attach the RunPod Network Volume before starting production workers."
            )

        root = volume / "models"
        cache_dir = volume / ".hf-cache"
        lock_path = volume / ".krea2-model-download.lock"
        ready_marker = root / ".krea2-models-ready-v582"

        unet_dir = root / "unet"
        clip_dir = root / "clip"
        vae_dir = root / "vae"
        for p in (unet_dir, clip_dir, vae_dir, cache_dir):
            p.mkdir(parents=True, exist_ok=True)

        print("[Krea2 bootstrap] v5.8.2 synchronous bootstrap", flush=True)
        print("[Krea2 bootstrap] Using Network Volume: /runpod-volume", flush=True)

        token = os.getenv("HF_TOKEN") or None
        models = [
            (
                "UNET",
                "ChrisColeTech/krea2-turbo-uncensored-v1.1-FP8",
                "split/diffusion_models/Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
                unet_dir / "Krea2_turbo_uncensored_edit_v1.1-fp8_scaled.safetensors",
            ),
            (
                "CLIP",
                "Comfy-Org/Krea-2",
                "text_encoders/qwen3vl_4b_fp8_scaled.safetensors",
                clip_dir / "qwen3vl_4b_fp8_scaled.safetensors",
            ),
            (
                "VAE",
                "Comfy-Org/Krea-2",
                "vae/qwen_image_vae.safetensors",
                vae_dir / "qwen_image_vae.safetensors",
            ),
        ]

        def file_state(label: str, path: Path) -> bool:
            exists = path.is_file()
            size = path.stat().st_size if exists else 0
            valid = exists and size > MIN_VALID_BYTES
            print(
                f"[Krea2 bootstrap] {label} EXISTS={exists} SIZE={size} VALID={valid} PATH={path}",
                flush=True,
            )
            return valid

        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("w") as lock_file:
            print("[Krea2 bootstrap] Waiting for model download lock...", flush=True)
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            print("[Krea2 bootstrap] Model download lock acquired.", flush=True)

            # Always inspect the real final destinations; never trust an old marker.
            for label, repo, filename, dest in models:
                if file_state(label, dest):
                    print(f"[Krea2 bootstrap] Exists: {dest}", flush=True)
                    continue

                # Remove a stale/invalid final file and stale partial copy.
                if dest.exists():
                    dest.unlink()
                tmp = Path(str(dest) + ".part")
                if tmp.exists():
                    tmp.unlink()

                print(f"[Krea2 bootstrap] Downloading {label}: {repo}/{filename}", flush=True)
                cached = Path(
                    hf_hub_download(
                        repo_id=repo,
                        filename=filename,
                        token=token,
                        cache_dir=str(cache_dir),
                    )
                )
                print(
                    f"[Krea2 bootstrap] HF cache ready {label}: {cached} SIZE={cached.stat().st_size}",
                    flush=True,
                )

                # Copy into the exact worker-comfyui Network Volume directory.
                shutil.copyfile(cached, tmp)
                with tmp.open("rb") as fh:
                    os.fsync(fh.fileno())
                tmp.replace(dest)

                if not file_state(label, dest):
                    raise RuntimeError(f"Downloaded {label} is missing/invalid at {dest}")
                print(f"[Krea2 bootstrap] Ready: {dest}", flush=True)

            print("[Krea2 bootstrap] Final model verification:", flush=True)
            all_valid = True
            for label, _, _, dest in models:
                all_valid = file_state(label, dest) and all_valid

            if not all_valid:
                raise RuntimeError("One or more Krea2 model files failed final verification")

            ready_marker.write_text(
                "Krea2 Turbo Edit v1.1 FP8 models verified by v5.8.2\n",
                encoding="utf-8",
            )
            print("[Krea2 bootstrap] KREA2_MODELS_READY", flush=True)
            print("[Krea2 bootstrap] MODEL_DOWNLOAD_COMPLETE", flush=True)

    except Exception as exc:
        # Keep ComfyUI alive so logs remain visible, but the diagnostic is explicit.
        print(
            f"[Krea2 bootstrap] FATAL MODEL BOOTSTRAP ERROR: {type(exc).__name__}: {exc}",
            flush=True,
        )
