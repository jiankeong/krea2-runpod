# Krea2 Turbo Edit v1.1 FP8 — RunPod Serverless v5

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
