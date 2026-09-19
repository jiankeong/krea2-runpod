# Krea2 RunPod Serverless v5.8.9

Fixes the v5.8.8 OpenCV installation regression.

- Keeps `.runpod/tests.json` unchanged.
- Keeps the worker-comfyui PyTorch/CUDA/numpy environment intact.
- Installs `opencv-python-headless==4.11.0.86` with `--no-deps --ignore-installed`.
- Verifies `cv2.CascadeClassifier` and Haar cascade data during Docker build.
- Verifies torch, CUDA and numpy versions are unchanged by the OpenCV repair.
- Keeps `AutoFacePreserveComposite` and the Network Volume Krea2 bootstrap.
