FROM runpod/worker-comfyui:5.8.6-base

USER root

# Keep worker-comfyui's official ENTRYPOINT/CMD.
# In production the custom-node import blocks until the three persistent
# Network Volume model files have been verified. Hub tests skip it entirely.
COPY custom_nodes/krea2_bootstrap /comfyui/custom_nodes/krea2_bootstrap

RUN echo "Krea2 v5.8.2 image built"
