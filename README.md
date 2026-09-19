# Krea2 RunPod Serverless v5.8.6

Adds Krea2 Identity Edit v1.2 support for stronger identity/face preservation during edits such as clothing changes.

Production runtime automatically verifies/downloads these files to the attached Network Volume:
- Krea2 Turbo uncensored FP8 UNET
- Qwen3-VL 4B FP8 Krea2 text encoder
- Qwen Image VAE
- `models/loras/Krea2/krea2_identity_edit_v1_2.safetensors`

The Docker image installs `lbouaraba/comfyui-krea2edit` custom nodes. `.runpod/tests.json` is intentionally retained for RunPod Hub smoke testing and uses `USE_MOCK_PIPELINE=1`, so Hub tests do not download model weights.

Attach the existing Network Volume at `/runpod-volume` for production.
