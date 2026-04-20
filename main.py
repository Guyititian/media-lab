from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import subprocess
import imageio_ffmpeg
import time

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"status": "media-lab running"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    input_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    palette_path = os.path.join(OUTPUT_DIR, f"{job_id}_palette.png")
    output_path = os.path.join(OUTPUT_DIR, f"{job_id}.gif")

    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    # STEP 1: Generate palette
    subprocess.run([
        ffmpeg_path,
        "-y",
        "-i",
        input_path,
        "-vf",
        "fps=15,scale=480:-1:flags=lanczos,palettegen",
        palette_path
    ])

    # STEP 2: Generate GIF
    subprocess.run([
        ffmpeg_path,
        "-y",
        "-i",
        input_path,
        "-i",
        palette_path,
        "-lavfi",
        "fps=15,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse",
        "-loop",
        "0",
        output_path
    ])

    # 🔥 WAIT until file is actually written
    timeout = 15  # seconds
    waited = 0

    while not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        time.sleep(1)
        waited += 1
        if waited >= timeout:
            return {
                "job_id": job_id,
                "error": "timeout waiting for gif"
            }

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}"
    }


@app.get("/download/{job_id}")
def download(job_id: str):
    path = os.path.join(OUTPUT_DIR, f"{job_id}.gif")

    if not os.path.exists(path):
        return {"error": "file not ready"}

    return FileResponse(path, media_type="image/gif", filename="output.gif")
