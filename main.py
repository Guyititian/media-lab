from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import subprocess
import imageio_ffmpeg

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
    output_path = os.path.join(OUTPUT_DIR, f"{job_id}.gif")

    # Save uploaded file
    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)

    # Get ffmpeg path (works on Render)
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    # Conversion command
    command = [
        ffmpeg_path,
        "-y",
        "-i",
        input_path,
        "-vf",
        "fps=12,scale=480:-1:flags=lanczos",
        "-loop",
        "0",
        output_path
    ]

    # Run ffmpeg
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # DEBUG LOGS (very important)
    print("====== FFMPEG COMMAND ======")
    print(" ".join(command))
    print("====== STDOUT ======")
    print(result.stdout)
    print("====== STDERR ======")
    print(result.stderr)

    # If conversion failed
    if not os.path.exists(output_path):
        return {
            "job_id": job_id,
            "error": "conversion failed",
            "ffmpeg_error": result.stderr[-1000:]
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
