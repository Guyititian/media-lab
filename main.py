from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import shutil
import subprocess
import imageio_ffmpeg

app = FastAPI()

# Get portable ffmpeg binary (NO system install needed)
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"status": "media-lab running", "mode": "gif-default"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    input_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    output_path = os.path.join(OUTPUT_DIR, f"{job_id}.gif")

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert to GIF using ffmpeg (bundled)
    command = [
        ffmpeg_path,
        "-i", input_path,
        "-vf", "fps=12,scale=480:-1:flags=lanczos",
        "-y",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}"
    }


@app.get("/download/{job_id}")
def download_gif(job_id: str):
    path = os.path.join(OUTPUT_DIR, f"{job_id}.gif")

    if not os.path.exists(path):
        return {"error": "file not ready"}

    return FileResponse(path, media_type="image/gif", filename=f"{job_id}.gif")
