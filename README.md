# Krea2 Turbo Edit v1.1 FP8 — RunPod Serverless v4

This version fixes the 30-minute RunPod GitHub Builder timeout by keeping large
model weights OUT of the Docker image.

## Required: Network Volume

Create and attach a RunPod Network Volume to the Serverless endpoint. The
official worker-comfyui image exposes `/runpod-volume` as an extra ComfyUI model
location. On the first worker boot, this image downloads Krea2 + text encoder +
VAE into that persistent volume. Later boots skip files that already exist.

Suggested volume size: 40 GB minimum; 50 GB gives more headroom.

## Endpoint

- Active workers: 0
- Max workers: 1 while testing
- GPU: start with >=24 GB VRAM; move up if inference OOMs
- Flash Boot: enabled
- Attach the Network Volume under Advanced
- Container disk: 20 GB is enough because model weights live on the volume

## Hugging Face token

If the ChrisColeTech model download returns 401/403, set `HF_TOKEN` as an
endpoint environment variable. Do NOT bake the token into the Dockerfile.

## First boot

The first worker boot downloads the model weights and can take several minutes.
Watch worker logs for `[Krea2 bootstrap]`. Once files are present on the Network
Volume, later workers skip the downloads.

## Request

The workflow expects a Base64 source image named `input.png`.

Edit prompt:
`workflow["16"]["inputs"]["prompt"]`

Seed:
`workflow["3"]["inputs"]["noise_seed"]`

Defaults: 1024x1024, 8 steps, CFG 1.0.
