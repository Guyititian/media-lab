from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import tempfile
import os

from core.presets import PRESETS
from tools.gif_motion import build_gif

router = APIRouter()

storage = {}


@router.post("/upload")
async def upload(file: UploadFile = File(...), preset: str = "balanced_v1"):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        preset_data = PRESETS.get(preset, PRESETS["balanced_v1"])
        vf = preset_data["vf"]

        build_gif(input_path, output_path, vf)

        if not os.path.exists(output_path):
            return {"error": "conversion failed"}

        with open(output_path, "rb") as f:
            storage[job_id] = f.read()

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}",
        "preset": preset
    }


@router.get("/download/{job_id}")
def download(job_id: str):
    if job_id not in storage:
        return {"error": "file not ready"}

    path = f"/tmp/{job_id}.gif"

    with open(path, "wb") as f:
        f.write(storage[job_id])

    return FileResponse(path, media_type="image/gif", filename="output.gif")
