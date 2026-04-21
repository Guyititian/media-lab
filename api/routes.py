from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import tempfile
import os

from tools.gif_motion import process
from core.presets import PRESETS

router = APIRouter()


# ------------------------
# STATUS
# ------------------------
@router.get("/")
def root():
    return {
        "status": "Media Lab running",
        "presets": list(PRESETS.keys())
    }


# ------------------------
# PRESET LIST (FOR FRONTEND)
# ------------------------
@router.get("/presets")
def get_presets():
    return PRESETS


# ------------------------
# GIF GENERATION
# ------------------------
@router.post("/upload")
async def upload(file: UploadFile = File(...), preset: str = "balanced_v1"):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        process(input_path, output_path, preset)

        if not os.path.exists(output_path):
            return {"error": "conversion failed"}

        with open(output_path, "rb") as f:
            data = f.read()

    # simple in-memory storage
    storage = router.storage if hasattr(router, "storage") else {}
    storage[job_id] = data
    router.storage = storage

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}"
    }


# ------------------------
# DOWNLOAD
# ------------------------
@router.get("/download/{job_id}")
def download(job_id: str):
    storage = getattr(router, "storage", {})

    if job_id not in storage:
        return {"error": "not ready"}

    path = f"/tmp/{job_id}.gif"

    with open(path, "wb") as f:
        f.write(storage[job_id])

    return FileResponse(path, media_type="image/gif")
