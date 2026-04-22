# api/routes.py

import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from tools.gif_motion import generate_gif
from core.presets import PRESETS

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

        # Validate tool
        if tool != "gif_motion":
            raise HTTPException(status_code=400, detail=f"Unsupported tool: {tool}")

        # Validate preset
        if preset not in PRESETS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid preset: {preset}. Must be one of {list(PRESETS.keys())}"
            )

        # Save upload
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Generate GIF
        result = generate_gif(input_path, preset)

        # Normalize response (IMPORTANT: flatten structure)
        return {
            "success": True,
            "output_url": result["output_url"]
        }

    except HTTPException as he:
        # Proper API error
        print("❌ ROUTE ERROR:", he.detail)
        return {
            "success": False,
            "error": he.detail
        }

    except Exception as e:
        # Unexpected failure
        print("❌ ROUTE ERROR:", str(e))
        return {
            "success": False,
            "error": str(e)
        }
