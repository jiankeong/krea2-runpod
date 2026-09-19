from __future__ import annotations
import cv2
import numpy as np
import torch

class AutoFacePreserveComposite:
    """Detect the largest face in the original image and composite original head pixels over edited output."""
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "original": ("IMAGE",),
            "edited": ("IMAGE",),
            "expand_x": ("FLOAT", {"default": 1.65, "min": 1.0, "max": 3.0, "step": 0.05}),
            "expand_top": ("FLOAT", {"default": 1.15, "min": 0.0, "max": 2.5, "step": 0.05}),
            "expand_bottom": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 2.0, "step": 0.05}),
            "feather": ("INT", {"default": 31, "min": 0, "max": 151, "step": 2}),
        }}
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "face_mask")
    FUNCTION = "composite"
    CATEGORY = "image/identity"

    def composite(self, original, edited, expand_x=1.65, expand_top=1.15, expand_bottom=0.35, feather=31):
        outputs, masks = [], []
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(cascade_path)
        for i in range(min(original.shape[0], edited.shape[0])):
            src = original[i].detach().cpu().numpy().astype(np.float32)
            dst = edited[i].detach().cpu().numpy().astype(np.float32)
            h, w = dst.shape[:2]
            if src.shape[:2] != (h, w):
                src = cv2.resize(src, (w, h), interpolation=cv2.INTER_LANCZOS4)
            rgb8 = np.clip(src * 255.0, 0, 255).astype(np.uint8)
            gray = cv2.cvtColor(rgb8, cv2.COLOR_RGB2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(40, 40))
            mask = np.zeros((h, w), dtype=np.float32)
            if len(faces):
                x, y, fw, fh = max(faces, key=lambda r: int(r[2]) * int(r[3]))
                cx = x + fw / 2.0
                halfw = fw * float(expand_x) / 2.0
                x1 = max(0, int(cx - halfw)); x2 = min(w, int(cx + halfw))
                y1 = max(0, int(y - fh * float(expand_top)))
                y2 = min(h, int(y + fh * (1.0 + float(expand_bottom))))
                center = ((x1 + x2)//2, (y1 + y2)//2)
                axes = (max(1,(x2-x1)//2), max(1,(y2-y1)//2))
                cv2.ellipse(mask, center, axes, 0, 0, 360, 1.0, -1)
                k = int(feather)
                if k > 0:
                    if k % 2 == 0: k += 1
                    mask = cv2.GaussianBlur(mask, (k, k), 0)
            # If no face is found, fail safe: return edited unchanged, mask=0.
            a = mask[..., None]
            out = src * a + dst * (1.0 - a)
            outputs.append(torch.from_numpy(np.clip(out, 0, 1)))
            masks.append(torch.from_numpy(mask))
        return (torch.stack(outputs, 0), torch.stack(masks, 0))

NODE_CLASS_MAPPINGS = {"AutoFacePreserveComposite": AutoFacePreserveComposite}
NODE_DISPLAY_NAME_MAPPINGS = {"AutoFacePreserveComposite": "Auto Face Preserve Composite"}
