FROM runpod/worker-comfyui:5.8.6-base

USER root

# IMPORTANT: Do not replace worker-comfyui's ENTRYPOINT/CMD.
# ComfyUI imports this tiny custom node during its normal startup.
# Hub tests set USE_MOCK_PIPELINE=1, so the import is instant.
# Production imports trigger a one-time download to the Network Volume.
COPY custom_nodes/krea2_bootstrap /comfyui/custom_nodes/krea2_bootstrap
