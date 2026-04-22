from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os
import uuid

from tools.gif_motion import generate_gif

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    tool: str = Form(...),
    preset: str = Form(...)
):
    try:
        # -------------------------
        # VALIDATE TOOL (future-proofing)
        # -------------------------
        if tool != "gif_motion":
            raise HTTPException(status_code=400, detail="Invalid tool")

        # -------------------------
        # SAVE INPUT FILE
        # -------------------------
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        input_filename = f"{uuid.uuid4()}_{file.filename}"
        input_path = os.path.join(UPLOAD_DIR, input_filename)

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # -------------------------
        # PROCESS THROUGH TOOL
        # -------------------------
        # IMPORTANT: MUST return dict ONLY
        result = generate_gif(
            input_path=input_path,
            preset=preset
        )

        # -------------------------
        # VALIDATE OUTPUT
        # -------------------------
        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail="Tool did not return dict response"
            )

        if "output_url" not in result:
            raise HTTPException(
                status_code=500,
                detail="Missing output_url from tool"
            )

        return result

    except Exception as e:
        print("❌ ROUTE ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
