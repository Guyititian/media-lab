from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import os

from core.presets import PRESETS
from tools.gif_motion import build_gif

router = APIRouter()


# ----------------------------
# UPLOAD (HARD DEBUG VERSION)
# ----------------------------
@router.post("/upload")
async def upload(file: UploadFile = File(...), preset: str = "balanced_v1"):

    job_id = str(uuid.uuid4())

    input_path = f"/tmp/{job_id}_input.mp4"
    output_path = f"/tmp/{job_id}_output.gif"

    # 🔥 HARD DEBUG LOGS
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔥 REQUEST RECEIVED")
    print("🔥 RAW PRESET:", preset)

    contents = await file.read()

    with open(input_path, "wb") as f:
        f.write(contents)

    # 🔥 STRICT VALIDATION (NO SILENT FALLBACKS)
    if preset not in PRESETS:
        print("❌ INVALID PRESET RECEIVED:", preset)
        return {
            "error": "invalid_preset",
            "received": preset,
            "allowed": list(PRESETS.keys())
        }

    vf = PRESETS[preset]["vf"]

    print("🔥 VALID PRESET CONFIRMED:", PRESETS[preset]["label"])
    print("🔥 VF SAMPLE:", vf[:150])
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

    build_gif(input_path, output_path, vf)

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        return {"error": "conversion_failed", "preset": preset}

    return {
        "job_id": job_id,
        "preset": preset,
        "download_url": f"/download/{job_id}"
    }


# ----------------------------
# DOWNLOAD
# ----------------------------
@router.get("/download/{job_id}")
def download(job_id: str):

    path = f"/tmp/{job_id}_output.gif"

    if not os.path.exists(path):
        return {"error": "file_not_found", "job_id": job_id}

    return FileResponse(
        path,
        media_type="image/gif",
        filename="output.gif"
    )
