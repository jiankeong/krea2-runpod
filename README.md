# Krea2 RunPod Serverless v5.8.5

Fixes the remaining `CLIPLoader type: krea2 not in list` failure.

## What changed
- Base remains `runpod/worker-comfyui:5.8.6-base` so the RunPod handler and lifecycle stay intact.
- During Docker build, current upstream ComfyUI source is overlaid onto `/comfyui`.
- Build fails unless both conditions are true:
  - `/comfyui/comfy/text_encoders/krea2.py` exists.
  - `/comfyui/nodes.py` contains the `krea2` CLIPLoader option.
- Existing synchronous Network Volume model bootstrap is retained.
- `.runpod/tests.json` is retained; Hub smoke tests still use `USE_MOCK_PIPELINE=1`.

## Expected build log
```
KREA2 CLIP TYPE: OK
KREA2 TEXT ENCODER: OK
```

## Expected production model log
Because the models already exist on the Network Volume, production should report `EXISTS=True` / `Exists:` for UNET, CLIP and VAE, followed by `KREA2_MODELS_READY`.

After deployment, retry the same `/runsync` workflow with `CLIPLoader` type set to `krea2`.
