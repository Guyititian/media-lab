from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import tempfile
import os

from core.presets import PRESETS
from tools.gif_motion import build_gif

router = APIRouter()


# ----------------------------
# UPLOAD
# ----------------------------
@router.post("/upload")
async def upload(file: UploadFile = File(...), preset: str = "balanced_v1"):
    job_id = str(uuid.uuid4())

    input_path = f"/tmp/{job_id}_input.mp4"
    output_path = f"/tmp/{job_id}_output.gif"

    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)

    if preset not in PRESETS:
        preset = "balanced_v1"

    vf = PRESETS[preset]["vf"]

    build_gif(input_path, output_path, vf)

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        return {"error": "conversion failed"}

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}",
        "preset": preset
    }


# ----------------------------
# DOWNLOAD
# ----------------------------
@router.get("/download/{job_id}")
def download(job_id: str):
    output_path = f"/tmp/{job_id}_output.gif"

    if not os.path.exists(output_path):
        return {"error": "file not ready"}

    return FileResponse(output_path, media_type="image/gif", filename="output.gif")
