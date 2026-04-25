import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from core.config import UPLOAD_DIR
from core.presets import PRESETS
from core.tool_schema import TOOL_DEFINITIONS
from core.validation import validate_upload_filename, validate_upload_size
from tools.gif_motion import generate_gif

router = APIRouter()


@router.get("/tools")
def get_tools():
    return {
        "success": True,
        "tools": TOOL_DEFINITIONS
    }


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    tool: str = Form(...),
    preset: str = Form(...)
):
    input_path = None

    try:
        if tool != "gif_motion":
            raise HTTPException(status_code=400, detail=f"Unsupported tool: {tool}")

        if preset not in PRESETS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid preset: {preset}. Must be one of {list(PRESETS.keys())}"
            )

        clean_filename = validate_upload_filename(file)
        data = await file.read()
        validate_upload_size(data)

        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{clean_filename}")

        with open(input_path, "wb") as saved_file:
            saved_file.write(data)

        result = generate_gif(input_path, preset)

        return {
            "success": True,
            "output_url": result["output_url"],
            "preset": preset
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    finally:
        if input_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError:
                pass
