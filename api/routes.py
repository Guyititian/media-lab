from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid

from tools.gif_motion import generate_gif

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    preset: str = Form("balanced_v1")
):
    try:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔥 REQUEST RECEIVED")
        print("🔥 RAW PRESET:", preset)

        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(input_path, "wb") as f:
            f.write(await file.read())

        output_path = generate_gif(input_path, preset, OUTPUT_DIR)

        filename = os.path.basename(output_path)

        return JSONResponse({
            "download_url": f"/download/{filename}"
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/download/{filename}")
def download(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(path):
        return JSONResponse({"error": "File not found"}, status_code=404)

    return FileResponse(path, media_type="image/gif", filename=filename)
