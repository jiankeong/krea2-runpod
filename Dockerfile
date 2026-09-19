FROM runpod/worker-comfyui:5.8.6-base

USER root

# Keep current upstream ComfyUI because Krea2 requires native core support.
RUN set -eux; \
    /opt/venv/bin/python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/Comfy-Org/ComfyUI/archive/refs/heads/master.tar.gz', '/tmp/comfyui.tar.gz')"; \
    mkdir -p /tmp/comfyui-new; \
    tar -xzf /tmp/comfyui.tar.gz --strip-components=1 -C /tmp/comfyui-new; \
    cp -a /tmp/comfyui-new/. /comfyui/; \
    /opt/venv/bin/python -m pip install --no-cache-dir -r /comfyui/requirements.txt; \
    rm -rf /tmp/comfyui-new /tmp/comfyui.tar.gz

# Install the official Krea2 Identity Edit custom nodes without requiring git.
RUN set -eux; \
    /opt/venv/bin/python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/lbouaraba/comfyui-krea2edit/archive/refs/heads/main.tar.gz', '/tmp/krea2edit.tar.gz')"; \
    mkdir -p /comfyui/custom_nodes/comfyui-krea2edit; \
    tar -xzf /tmp/krea2edit.tar.gz --strip-components=1 -C /comfyui/custom_nodes/comfyui-krea2edit; \
    rm -f /tmp/krea2edit.tar.gz

# Build-time sanity checks: native Krea2 + Identity Edit nodes must exist.
RUN /opt/venv/bin/python - <<'PY'
import pathlib, sys
assert pathlib.Path('/comfyui/comfy/text_encoders/krea2.py').is_file()
assert pathlib.Path('/comfyui/custom_nodes/comfyui-krea2edit/__init__.py').is_file()
sys.path.insert(0, '/comfyui')
print('KREA2 CORE: OK')
print('KREA2 IDENTITY EDIT NODES: OK')
PY

# Runtime bootstrap stores large weights on the attached Network Volume.
COPY custom_nodes/krea2_bootstrap /comfyui/custom_nodes/krea2_bootstrap
COPY custom_nodes/auto_face_preserve /comfyui/custom_nodes/auto_face_preserve
# v5.8.9: repair cv2 WITHOUT allowing pip to resolve/upgrade any dependency.
# In particular, do not touch torch/CUDA/numpy from worker-comfyui.
RUN set -eux; \
    TORCH_BEFORE=$(/opt/venv/bin/python -c "import torch; print(torch.__version__)"); \
    CUDA_BEFORE=$(/opt/venv/bin/python -c "import torch; print(torch.version.cuda)"); \
    NUMPY_BEFORE=$(/opt/venv/bin/python -c "import numpy; print(numpy.__version__)"); \
    echo "Before OpenCV: torch=${TORCH_BEFORE} cuda=${CUDA_BEFORE} numpy=${NUMPY_BEFORE}"; \
    /opt/venv/bin/python -m pip install --no-cache-dir --no-deps --ignore-installed "opencv-python-headless==4.11.0.86"; \
    /opt/venv/bin/python -c "import cv2; assert hasattr(cv2, 'CascadeClassifier'), cv2.__file__; assert hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'); print('OpenCV:', cv2.__version__, cv2.__file__)"; \
    test "$TORCH_BEFORE" = "$(/opt/venv/bin/python -c 'import torch; print(torch.__version__)')"; \
    test "$CUDA_BEFORE" = "$(/opt/venv/bin/python -c 'import torch; print(torch.version.cuda)')"; \
    test "$NUMPY_BEFORE" = "$(/opt/venv/bin/python -c 'import numpy; print(numpy.__version__)')"

RUN echo "Krea2 RunPod v5.8.9 auto-face-preserve build complete"
