# Krea2 RunPod Serverless v5.8.8

Adds automatic face preservation for single-image Krea2 edits.

- Input can remain a single `input.png`; no user-supplied mask is required.
- `AutoFacePreserveComposite` detects the largest frontal face from the original image, expands the protected region toward hair/head, feathers the boundary, and composites original pixels over the Krea2 edited result.
- Krea2 base edit remains 8 steps / CFG 1.
- Existing Network Volume model paths are unchanged.
- `.runpod/tests.json` is retained for RunPod Hub smoke testing.

For a workflow, connect the original `LoadImage` and final `VAEDecode` to `AutoFacePreserveComposite`, then connect its `image` output to `SaveImage`.


## v5.8.8
Fixes incomplete/conflicting cv2 installation that caused `CascadeClassifier` to be missing. The Docker build now removes conflicting OpenCV packages, installs one complete headless wheel, and fails the build unless `CascadeClassifier` and Haar cascade data are available. API/workflow schema is unchanged from v5.8.7.
