FROM runpod/worker-comfyui:5.8.6-base

USER root
WORKDIR /workspace

# huggingface_hub is already included by the base image; avoid changing the
# Transformers/Hugging Face dependency set during Hub builds.
COPY handler.py /workspace/handler.py
COPY rp_handler.py /workspace/rp_handler.py
COPY scripts /workspace/scripts

# Keep the official worker-comfyui runtime intact. Hub can discover handler.py,
# while tests use USE_MOCK_PIPELINE=1 and therefore never fetch model weights.
