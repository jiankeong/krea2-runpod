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
