# Krea2 Turbo Edit v1.1 FP8 — RunPod Serverless

[![RunPod](https://api.runpod.io/badge/jiankeong/qwen-image-edit-runpod)](https://console.runpod.io/)

Target model: `ChrisColeTech/krea2-turbo-uncensored-v1.1-FP8`

This build uses:
- Krea2 Turbo Edit v1.1 FP8 transformer
- `qwen3vl_4b_fp8_scaled.safetensors`
- `qwen_image_vae.safetensors`
- RunPod `worker-comfyui`

## Deploy

Push the contents of this folder to the root of your GitHub repository and
rebuild the RunPod Serverless endpoint.

Recommended first test:
- GPU VRAM: 24 GB or more; if the worker OOMs during model loading/inference,
  select a larger VRAM GPU.
- Active workers: 0
- Max workers: 1
- Container disk: 40 GB+

The target Hugging Face repository is marked Not-For-All-Audiences. If the
Docker build returns 401/403 for the transformer, create a Hugging Face read
token with access to the repository and provide it to the Docker build as
`HF_TOKEN`.

## API input

`worker-comfyui` expects an API-format ComfyUI workflow plus input images.
The workflow expects the uploaded image to be named `input.png`.

Prompt:
`workflow["16"]["inputs"]["prompt"]`

Seed:
`workflow["3"]["inputs"]["noise_seed"]`

Default settings:
- 1024x1024
- 8 steps
- CFG 1.0
- Euler / simple

For a request, put a Base64 encoded source image in `input.images[0].image`.
