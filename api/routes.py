from fastapi import APIRouter, UploadFile, File
import uuid
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

    # ----------------------------
    # DEBUG (CRITICAL FOR YOUR ISSUE)
    # ----------------------------
    print("🔥 PRESET RECEIVED:", preset)

    # Save upload
    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)

    # ----------------------------
    # VALIDATE PRESET (NO SILENT FALLBACK)
    # ----------------------------
    if preset not in PRESETS:
        print("❌ INVALID PRESET:", preset)
        return {
            "job_id": job_id,
            "error": f"invalid preset: {preset}"
        }

    # ----------------------------
    # GET FILTER PIPELINE
    # ----------------------------
    vf = PRESETS[preset]["vf"]

    print("🔥 APPLYING PRESET:", PRESETS[preset]["label"])
    print("🔥 VF START:", vf[:120])

    # ----------------------------
    # CRITICAL: PASS VF INTO PIPELINE
    # ----------------------------
    build_gif(input_path, output_path, vf)

    # ----------------------------
    # SAFETY CHECK
    # ----------------------------
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
# DOWNLOAD
# ----------------------------
@router.get("/download/{job_id}")
def download(job_id: str):
    path = f"/tmp/{job_id}_output.gif"

    if not os.path.exists(path):
        return {"error": "file_not_found"}

    from fastapi.responses import FileResponse
    return FileResponse(path, media_type="image/gif", filename="output.gif")
