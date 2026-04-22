from fastapi import APIRouter, UploadFile, File, Form
import uuid
import shutil
import os

router = APIRouter()

# Import your tools safely (do NOT change existing tool logic files)
# from tools.gif_motion import gif_motion
# from tools.upscale import upscale

@router.post("/api/run")
async def run_tool(
    tool: str = Form(...),
    file: UploadFile = File(...)
):
    # -------------------------
    # CREATE WORKING FILE PATHS
    # -------------------------
    file_id = str(uuid.uuid4())

    input_path = f"/tmp/{file_id}_{file.filename}"
    output_path = f"outputs/{file_id}.gif"

    os.makedirs("outputs", exist_ok=True)

    # -------------------------
    # SAVE UPLOADED FILE
    # -------------------------
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # -------------------------
    # TOOL ROUTING (SAFE HOOKS)
    # -------------------------
    if tool == "gif_motion":
        # Replace this with your real function later
        # gif_motion(input_path, output_path)
        shutil.copy(input_path, output_path)

    elif tool == "upscale":
        # upscale(input_path, output_path)
        shutil.copy(input_path, output_path)

    else:
        # fallback safe behavior
        shutil.copy(input_path, output_path)

    # -------------------------
    # PUBLIC OUTPUT URL
    # -------------------------
    output_url = f"https://YOUR-RENDER-SERVICE.onrender.com/outputs/{file_id}.gif"

    return {
        "tool": tool,
        "output_url": output_url
    }
