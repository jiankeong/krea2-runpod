# Krea2 RunPod Serverless v5.8.3

Fixes the remaining Krea2 CLIP loader problem seen on RunPod worker-comfyui 5.8.6-base.

## Changes

- Keeps `runpod/worker-comfyui:5.8.6-base` and its official RunPod handler/ENTRYPOINT.
- Upgrades ComfyUI core to **v0.26.0**, which includes Krea2 support (`CLIPLoader` type `krea2`).
- Keeps the v5.8.2 synchronous Network Volume bootstrap.
- Reuses existing models under `/runpod-volume/models/{unet,clip,vae}`; they are not re-downloaded when valid.
- Keeps `.runpod/tests.json` and `USE_MOCK_PIPELINE=1` Hub-test bypass.

## Expected production startup

Existing Network Volume should show `Exists:` for UNET/CLIP/VAE followed by:

```
[Krea2 bootstrap] KREA2_MODELS_READY
[Krea2 bootstrap] MODEL_DOWNLOAD_COMPLETE
```

Then ComfyUI should accept `CLIPLoader` with:

```json
{
  "clip_name": "qwen3vl_4b_fp8_scaled.safetensors",
  "type": "krea2",
  "device": "default"
}
```
