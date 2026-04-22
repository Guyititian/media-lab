# api/routes.py

import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form
from tools.gif_motion import generate_gif, PRESETS

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    tool: str = Form(...),
    preset: str = Form(...)
):
    try:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔥 ROUTE REQUEST")
        print(f"🔥 TOOL: {tool}")
        print(f"🔥 PRESET: {preset}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 1. Validate tool
        if tool != "gif_motion":
            return {"error": f"Unsupported tool: {tool}"}

        # 2. Validate preset exists (NO parsing)
        if preset not in PRESETS:
            return {
                "error": f"Invalid preset: {preset}. Must be one of {list(PRESETS.keys())}"
            }

        # 3. Save upload
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(input_path, "wb") as f:
            f.write(await file.read())

        # 4. Generate GIF (ALL logic handled downstream)
        output_url = generate_gif(input_path, preset)

        return {
            "output_url": output_url
        }

    except Exception as e:
        print("❌ ROUTE ERROR:", str(e))
        return {"error": str(e)}
