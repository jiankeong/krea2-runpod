"""RunPod Hub validation handler. Production runtime uses worker-comfyui's handler."""
import runpod

def handler(job):
    data = job.get("input") or {}
    if "workflow" not in data:
        return {"error": "Missing input.workflow"}
    return {"status": "Repository validation OK"}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
