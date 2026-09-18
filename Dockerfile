FROM runpod/worker-comfyui:5.8.6-base

USER root
WORKDIR /workspace

# Keep the base image's Python/Hugging Face dependency set intact.
COPY handler.py /workspace/handler.py
COPY rp_handler.py /workspace/rp_handler.py
COPY scripts /workspace/scripts

RUN chmod +x /workspace/scripts/start-krea2.sh

# Hub tests set USE_MOCK_PIPELINE=1 and skip model bootstrap.
# Production workers bootstrap the persistent Network Volume first,
# then hand control back to the official worker-comfyui start script.
ENTRYPOINT ["/workspace/scripts/start-krea2.sh"]
