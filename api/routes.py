from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import os

from core.presets import PRESETS
from core.tool_schema import TOOL_DEFINITIONS
from tools.gif_motion import build_gif

router = APIRouter()

# Simple in-memory storage (MVP safe)
storage = {}


# ----------------------------
# UPLOAD ENDPOINT
# ----------------------------
@router.post("/upload")
async def upload(file: UploadFile = File(...), preset: str = "balanced_v1"):
    job_id = str(uuid.uuid4())

    input_path = f"/tmp/{job_id}_input.mp4"
    output_path = f"/tmp/{job_id}_output.gif"

    # Save uploaded file
    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)

    # Validate preset
    if preset not in PRESETS:
        preset = "balanced_v1"

    vf = PRESETS[preset]["vf"]

    # Run GIF pipeline
    build_gif(input_path, output_path, vf)

    # Validate output
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        return {
            "job_id": job_id,
            "error": "conversion_failed"
        }

    # Store result in memory
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

    output_path = f"/tmp/{job_id}_output.gif"

    with open(output_path, "wb") as f:
        f.write(storage[job_id])

    return FileResponse(
        output_path,
        media_type="image/gif",
        filename="output.gif"
    )


# ----------------------------
# TOOLS ENDPOINT (FOR MEDIA-TILES UI)
# ----------------------------
@router.get("/tools")
def tools():
    return TOOL_DEFINITIONS
