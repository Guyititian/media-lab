from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import os

from core.presets import PRESETS
from core.tool_schema import TOOL_DEFINITIONS
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
    final_path = f"/tmp/{job_id}.gif"

    # DEBUG (THIS IS IMPORTANT — CONFIRMS FRONTEND VALUE)
    print("🔥 PRESET RECEIVED:", preset)

    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)

    # HARD VALIDATION (DO NOT SILENT FALLBACK ANYMORE)
    if preset not in PRESETS:
        return {
            "job_id": job_id,
            "error": f"invalid_preset_received: {preset}"
        }

    vf = PRESETS[preset]["vf"]

    build_gif(input_path, output_path, vf)

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        return {
            "job_id": job_id,
            "error": "conversion_failed"
        }

    with open(output_path, "rb") as f:
        data = f.read()

    with open(final_path, "wb") as f:
        f.write(data)

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}",
        "preset": preset,
        "tool": TOOL_DEFINITIONS["gif_motion"]
    }


# ----------------------------
# DOWNLOAD
# ----------------------------
@router.get("/download/{job_id}")
def download(job_id: str):
    path = f"/tmp/{job_id}.gif"

    if not os.path.exists(path):
        return {"error": "file_not_ready"}

    return FileResponse(
        path,
        media_type="image/gif",
        filename="output.gif"
    )


# ----------------------------
# TOOLS
# ----------------------------
@router.get("/tools")
def tools():
    return TOOL_DEFINITIONS
