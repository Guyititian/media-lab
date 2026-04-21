from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import tempfile
import os

from core.presets import PRESETS
from tools.gif_motion import build_gif

router = APIRouter()


# ----------------------------
# UPLOAD ENDPOINT
# ----------------------------
@router.post("/upload")
async def upload(file: UploadFile = File(...), preset: str = "balanced_v1"):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        # get preset config
        if preset not in PRESETS:
            preset = "balanced_v1"

        preset_data = PRESETS[preset]
        vf = preset_data["vf"]

        # build gif using selected preset
        build_gif(input_path, output_path, vf)

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {"job_id": job_id, "error": "conversion failed"}

        with open(output_path, "rb") as f:
            gif_data = f.read()

    # simple in-memory storage
    if not hasattr(router, "storage"):
        router.storage = {}

    router.storage[job_id] = gif_data

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}",
        "preset": preset
    }


# ----------------------------
# DOWNLOAD ENDPOINT
# ----------------------------
@router.get("/download/{job_id}")
def download(job_id: str):
    storage = getattr(router, "storage", {})

    if job_id not in storage:
        return {"error": "file not ready"}

    path = f"/tmp/{job_id}.gif"

    with open(path, "wb") as f:
        f.write(storage[job_id])

    return FileResponse(path, media_type="image/gif", filename="output.gif")
