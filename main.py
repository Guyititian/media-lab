from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import imageio_ffmpeg
import subprocess

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
    # Save uploaded file
    job_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    output_path = os.path.join(OUTPUT_DIR, f"{job_id}.gif")

    contents = await file.read()

    with open(input_path, "wb") as f:
        f.write(contents)

    # Get ffmpeg path from imageio-ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    # Convert video → GIF
    command = [
        ffmpeg_path,
        "-y",
        "-i",
        input_path,
        "-vf",
        "fps=12,scale=480:-1:flags=lanczos",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
