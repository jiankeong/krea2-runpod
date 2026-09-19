# Krea2 Turbo Edit v1.1 FP8 — RunPod Serverless v5.1

## What changed from v4

- `.runpod/tests.json` is retained and uses `USE_MOCK_PIPELINE=1`.
- Hub smoke tests do not download model weights.
- Hub test timeout is 300000 ms.
- `hub.json` follows the richer RunPod Hub configuration shape from the supplied working reference.
- Network Volume model directories match worker-comfyui's published paths:
  - diffusion model -> `/runpod-volume/models/unet/`
  - text encoder -> `/runpod-volume/models/clip/`
  - VAE -> `/runpod-volume/models/vae/`
- No `pip install -U huggingface_hub`, avoiding the prior Transformers dependency conflict.
- Model weights are not baked into the Docker image.

## Important

Attach a Network Volume (50 GB+ recommended) at deployment. Do not set
`USE_MOCK_PIPELINE=1` on the production endpoint; that variable is only for
RunPod Hub tests.

The included `workflow_api.json` is the Krea2 workflow template. The Docker
base remains the official `runpod/worker-comfyui:5.8.6-base`.

## v5.1

Removed the fixed `gpuTypeId` from `.runpod/tests.json` so RunPod Hub can allocate any available GPU compatible with the allowed CUDA versions. The smoke test still uses `USE_MOCK_PIPELINE=1` and does not load Krea2 weights.

## v5.2

Hub smoke-test scheduling update:
- Explicit test GPU: `NVIDIA L4`
- Expanded `allowedCudaVersions` from 12.4 through 13.3
- `USE_MOCK_PIPELINE=1` remains enabled for Hub tests, so Krea2 weights are not loaded during the smoke test.

## v5.3

Hub smoke test now sends a real, model-free ComfyUI workflow:
`EmptyImage (64x64) -> SaveImage`.

This fixes `prompt_no_outputs` caused by the previous empty `{}` workflow.
The Hub test does not load Krea2, Qwen3VL, or the VAE.

## v5.4

Fixed `.runpod/hub.json` `gpuIds` for Endpoint creation.
RunPod expects GPU pool IDs rather than GPU display names.

Allowed pools:
`ADA_24,AMPERE_24,ADA_48_PRO,AMPERE_48,ADA_80_PRO,AMPERE_80`

The working Hub smoke-test configuration in `.runpod/tests.json` is unchanged.


## v5.6

This version removes the v5.5 ENTRYPOINT wrapper.

The official `runpod/worker-comfyui:5.8.6-base` startup lifecycle is preserved.
A minimal ComfyUI custom node (`custom_nodes/krea2_bootstrap`) performs model
bootstrap when ComfyUI loads custom nodes:

- Hub smoke tests set `USE_MOCK_PIPELINE=1`, so no model download occurs.
- Production leaves it at `0` (default), so missing weights are downloaded to
  `/runpod-volume/models/{unet,clip,vae}` before ComfyUI finishes startup.
- Existing model files on the Network Volume are reused.

Production requires a Network Volume mounted at `/runpod-volume`.


## v5.8 crash fix

- The bootstrap hook can no longer raise an exception that kills ComfyUI.
- Missing `/runpod-volume` falls back to ephemeral `/comfyui/models`.
- Large model downloads run in a background thread, so Serverless readiness is
  not blocked by Hugging Face downloads.
- Look for `MODEL_DOWNLOAD_COMPLETE` before sending the first Krea2 workflow.
- The official worker-comfyui ENTRYPOINT/CMD remains untouched.


## v5.8 notes

- Network Volume model downloads are serialized with a file lock, preventing multiple autoscaled workers from racing on the same files.
- Hugging Face cache is stored on `/runpod-volume/.hf-cache`, avoiding pressure on the 40 GB ephemeral container disk.
- RunPod worker-comfyui intentionally exposes `/runpod-volume/models/unet` as ComfyUI `diffusion_models` and `/runpod-volume/models/clip` as `text_encoders`; those legacy directory names are therefore correct for this image.
- Wait for `[Krea2 bootstrap] MODEL_DOWNLOAD_COMPLETE` before sending a real Krea2 workflow.

## v5.8.1

- Hub smoke-test isolation hardened: when `USE_MOCK_PIPELINE=1`, the custom node returns through the minimal path before importing `fcntl`, `huggingface_hub`, filesystem helpers, or starting any thread.
- Production behavior keeps the v5.8 Network Volume lock and persistent Hugging Face cache.
- `.runpod/tests.json` remains required and unchanged from the known-good v5.7 smoke workflow.

## v5.8.2

- Production bootstrap is synchronous during ComfyUI custom-node import. ComfyUI will not become API-ready until all three Krea2 files exist in the exact Network Volume model directories.
- `.runpod/tests.json` is retained. `USE_MOCK_PIPELINE=1` still bypasses all downloads during Hub smoke tests.
- An old ready marker is never trusted; every startup checks the actual final file path and size.
- Adds explicit `UNET/CLIP/VAE EXISTS=... SIZE=... VALID=... PATH=...` diagnostics.
- Downloads are serialized with the Network Volume file lock and copied atomically through `.part` files.
- Successful production startup prints `KREA2_MODELS_READY` followed by `MODEL_DOWNLOAD_COMPLETE`.
