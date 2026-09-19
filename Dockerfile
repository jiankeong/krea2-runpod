FROM runpod/worker-comfyui:5.8.6-base

USER root

# worker-comfyui 5.8.6 currently ships a ComfyUI core that does not expose
# CLIPLoader type "krea2" in this runtime. Krea 2 requires ComfyUI >= 0.26.0.
# Upgrade only the ComfyUI core while preserving RunPod's handler/startup.
RUN set -eux; \
    curl -fL "https://github.com/comfyanonymous/ComfyUI/archive/refs/tags/v0.26.0.tar.gz" -o /tmp/comfyui.tar.gz; \
    mkdir -p /tmp/comfyui-new; \
    tar -xzf /tmp/comfyui.tar.gz --strip-components=1 -C /tmp/comfyui-new; \
    cp -a /tmp/comfyui-new/. /comfyui/; \
    /opt/venv/bin/python -m pip install --no-cache-dir -r /comfyui/requirements.txt; \
    rm -rf /tmp/comfyui-new /tmp/comfyui.tar.gz

# Keep worker-comfyui's official ENTRYPOINT/CMD.
# Production blocks during custom-node import until persistent models are valid.
# Hub smoke tests skip the bootstrap completely via USE_MOCK_PIPELINE=1.
COPY custom_nodes/krea2_bootstrap /comfyui/custom_nodes/krea2_bootstrap

RUN /opt/venv/bin/python - <<'PY'
from pathlib import Path
p = Path('/comfyui/comfy/sd.py')
print('ComfyUI 0.26.0 core installed:', p.exists())
PY

RUN echo "Krea2 v5.8.3 image built - ComfyUI core v0.26.0"
