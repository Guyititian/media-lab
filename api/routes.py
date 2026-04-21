from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import tempfile
import os

from core.presets import PRESETS
from core.tool_schema import TOOL_DEFINITIONS
from tools.gif_motion import build_gif

router = APIRouter()

# simple in-memory storage (will later upgrade to job system if needed)
storage = {}


# ----------------------------
# UPLOAD ENDPOINT
# ----------------------------
@router.post("/upload")
async def upload(file: UploadFile = File(...), preset: str = "balanced_v1"):
    job_id = str(uuid.uuid4())

    input_path = f"/tmp/{job_id}_input.mp4"
    output_path = f"/tmp/{job_id}_output.gif"

    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)

    # validate preset
    if preset not in PRESETS:
        preset = "balanced_v1"

    vf = PRESETS[preset]["vf"]

    # run pipeline
    build_gif(input_path, output_path, vf)

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        return {
            "job_id": job_id,
            "error": "conversion_failed"
        }

    with open(output_path, "rb") as f:
        storage[job_id] = f.read()

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}",
        "preset": preset,
        "tool": TOOL_DEFINITIONS["gif_motion"]
    }


# ----------------------------
# DOWNLOAD ENDPOINT
# ----------------------------
@router.get("/download/{job_id}")
def download(job_id: str):
    if job_id not in storage:
        return {"error": "file_not_ready"}

    path = f"/tmp/{job_id}.gif"

    with open(path, "wb") as f:
        f.write(storage[job_id])

    return FileResponse(path, media_type="image/gif", filename="output.gif")


# ----------------------------
# TOOLS LIST (FOR MEDIA-TILES UI)
# ----------------------------
@router.get("/tools")
def tools():
    return TOOL_DEFINITIONS
