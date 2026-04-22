from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import uuid

from tools.gif_motion import generate_gif

router = APIRouter()


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    tool: str = Form(...),
    preset: str = Form(...)
):
    try:
        if tool != "gif_motion":
            raise HTTPException(status_code=400, detail="Invalid tool")

        # Save upload
        upload_id = str(uuid.uuid4())
        input_path = f"uploads/{upload_id}_{file.filename}"

        os.makedirs("uploads", exist_ok=True)
        os.makedirs("outputs", exist_ok=True)

        with open(input_path, "wb") as f:
            f.write(await file.read())

        output_id = str(uuid.uuid4())
        output_path = f"outputs/{output_id}.gif"

        # IMPORTANT: no PRESETS handling here anymore
        result_path = generate_gif(
            input_path=input_path,
            output_path=output_path,
            preset_name=preset
        )

        return {
            "output_url": "/" + result_path
        }

    except Exception as e:
        print(f"❌ ROUTE ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
