FROM runpod/worker-comfyui:5.8.6-base

USER root

# Keep the base image's compatible Hugging Face stack.
RUN pip install --no-cache-dir "huggingface_hub>=0.36,<1.0"

COPY scripts/bootstrap_models.py /opt/krea2/bootstrap_models.py
COPY scripts/start-krea2.sh /opt/krea2/start-krea2.sh

RUN chmod +x /opt/krea2/start-krea2.sh

# worker-comfyui already knows /runpod-volume as an extra ComfyUI model path.
# We wrap its original CMD so models are bootstrapped into the persistent
# Network Volume before the official worker starts.
ENTRYPOINT ["/opt/krea2/start-krea2.sh"]
