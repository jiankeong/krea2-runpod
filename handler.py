"""
RunPod Hub validation entrypoint.

The production container inherits the tested RunPod worker-comfyui handler.
This file exists for Hub repository validation; Dockerfile intentionally does
not COPY it into the image.
"""
import runpod

def handler(job):
    data = job.get("input") or {}
    if "workflow" not in data:
        return {"error": "Missing input.workflow"}
    return {"status": "Repository handler validated. Production image uses worker-comfyui handler."}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
