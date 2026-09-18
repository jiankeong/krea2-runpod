FROM runpod/worker-comfyui:5.8.6-base

USER root

# Keep the official worker-comfyui ENTRYPOINT/CMD intact.
# This custom node only performs a non-fatal background model bootstrap.
COPY custom_nodes/krea2_bootstrap /comfyui/custom_nodes/krea2_bootstrap

RUN echo "Krea2 v5.8.1 image built"
