from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import os

from core.presets import PRESETS
from tools.gif_motion import build_gif

router = APIRouter()


# ----------------------------
# UPLOAD ROUTE
# ----------------------------
@router.post("/upload")
async def upload(file: UploadFile = File(...), preset: str = "balanced_v1"):

    job_id = str(uuid.uuid4())

    input_path = f"/tmp/{job_id}_input.mp4"
    output_path = f"/tmp/{job_id}_output.gif"

    print("🔥 PRESET RECEIVED:", preset)

    # Save uploaded file
    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)

    # Validate preset
    if preset not in PRESETS:
        print("❌ INVALID PRESET:", preset)
        return {
            "job_id": job_id,
            "error": f"invalid preset: {preset}"
        }

    vf = PRESETS[preset]["vf"]

    print("🔥 APPLYING PRESET:", PRESETS[preset]["label"])
    print("🔥 VF START:", vf[:120])

    # Run FFmpeg pipeline
    build_gif(input_path, output_path, vf)

    # Validate output exists
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        return {
            "job_id": job_id,
            "error": "conversion_failed"
        }

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}",
        "preset": preset
    }


# ----------------------------
# DOWNLOAD ROUTE
# ----------------------------
@router.get("/download/{job_id}")
def download(job_id: str):

    path = f"/tmp/{job_id}_output.gif"

    if not os.path.exists(path):
        return {
            "error": "file_not_found",
            "job_id": job_id
        }

    return FileResponse(
        path,
        media_type="image/gif",
        filename="output.gif"
    )


# ----------------------------
# OPTIONAL: TOOL DISCOVERY
# ----------------------------
@router.get("/tools")
def tools():
    return {
        "gif_motion": {
            "name": "GIF Motion",
            "presets": list(PRESETS.keys())
        }
    }
