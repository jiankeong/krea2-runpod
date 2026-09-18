FROM runpod/worker-comfyui:5.8.6-base

USER root

# Do not override ENTRYPOINT/CMD from worker-comfyui.
# The bootstrap hook is deliberately non-fatal and downloads in background.
COPY custom_nodes/krea2_bootstrap /comfyui/custom_nodes/krea2_bootstrap

RUN echo "Krea2 v5.7 image built"
