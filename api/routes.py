from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
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
    tool: str = Form("gif_motion"),
    preset: str = Form("balanced_v1")
):
    try:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔥 TOOL:", tool)
        print("🔥 RAW PRESET:", preset)

        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(input_path, "wb") as f:
            f.write(await file.read())

        output_path = generate_gif(input_path, preset, OUTPUT_DIR)

        filename = os.path.basename(output_path)

        return JSONResponse({
            "output_url": f"/outputs/{filename}"
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return JSONResponse({"error": str(e)}, status_code=500)
