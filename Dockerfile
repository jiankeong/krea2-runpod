FROM runpod/worker-comfyui:5.8.6-base

USER root

# v5.8.5: overlay current upstream ComfyUI without relying on curl/git.
# Python is already present in worker-comfyui, so urllib avoids the build
# failure caused by minimal base images that do not provide curl.
RUN set -eux; \
    /opt/venv/bin/python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/Comfy-Org/ComfyUI/archive/refs/heads/master.tar.gz', '/tmp/comfyui.tar.gz')"; \
    mkdir -p /tmp/comfyui-new; \
    tar -xzf /tmp/comfyui.tar.gz --strip-components=1 -C /tmp/comfyui-new; \
    cp -a /tmp/comfyui-new/. /comfyui/; \
    /opt/venv/bin/python -m pip install --no-cache-dir -r /comfyui/requirements.txt; \
    rm -rf /tmp/comfyui-new /tmp/comfyui.tar.gz

# Fail the image build if the installed ComfyUI core does not really contain
# Krea2 CLIP support. This prevents a deployable image with type=krea2 missing.
RUN /opt/venv/bin/python - <<'PY'
import pathlib
import sys

nodes = pathlib.Path('/comfyui/nodes.py')
krea2 = pathlib.Path('/comfyui/comfy/text_encoders/krea2.py')

assert nodes.is_file(), f'Missing {nodes}'
assert krea2.is_file(), f'Missing {krea2}'

text = nodes.read_text(encoding='utf-8')
assert '"krea2"' in text or "'krea2'" in text, 'CLIPLoader krea2 option missing from nodes.py'

sys.path.insert(0, '/comfyui')
print('KREA2 CLIP TYPE: OK')
print('KREA2 TEXT ENCODER: OK')
PY

# Keep the proven synchronous Network Volume model bootstrap from v5.8.2+.
COPY custom_nodes/krea2_bootstrap /comfyui/custom_nodes/krea2_bootstrap

RUN echo "Krea2 v5.8.5 image built with verified upstream Krea2 core support"
