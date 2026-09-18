FROM runpod/worker-comfyui:5.8.6-base

USER root

RUN pip install --no-cache-dir -U huggingface_hub

COPY scripts/download_models.py /tmp/download_models.py

ARG HF_TOKEN=""
ENV HF_TOKEN=${HF_TOKEN}

RUN python /tmp/download_models.py
