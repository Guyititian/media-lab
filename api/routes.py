from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os
import uuid

from tools.gif_motion import generate_gif, PRESETS

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -----------------------------
# PRESET RESOLVER (FIX FOR YOUR ERROR)
# -----------------------------
def resolve_preset(preset_name: str):
    """
    Converts frontend string → backend preset dict
    """

    if preset_name in PRESETS:
        return PRESETS[preset_name]

    # backwards compatibility layer (VERY IMPORTANT)
    legacy_map = {
        "balanced": "balanced_v1",
        "fluid_motion": "fluid_motion_v1",
    }

    if preset_name in legacy_map:
        return PRESETS[legacy_map[preset_name]]

    raise HTTPException(
        status_code=400,
        detail=f"Invalid preset: {preset_name}. Must be one of {list(PRESETS.keys())}"
    )


# -----------------------------
# MAIN ROUTE
# -----------------------------
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    tool: str = Form(...),
    preset: str = Form(...),
):
    try:
        # validate tool
        if tool != "gif_motion":
            raise HTTPException(status_code=400, detail="Invalid tool")

        # save upload
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # resolve preset HERE (critical fix)
        preset_dict = resolve_preset(preset)

        # run engine
        output_url = generate_gif(input_path, preset_dict)

        return {"output_url": output_url}

    except HTTPException as e:
        raise e

    except Exception as e:
        print("❌ ROUTE ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
