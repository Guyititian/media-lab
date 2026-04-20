from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import uuid
import os
import subprocess

app = FastAPI()

INPUT_DIR = "input"
OUTPUT_DIR = "output"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"status": "media-lab running"}


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    input_path = f"{INPUT_DIR}/{job_id}.mp4"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"job_id": job_id}


@app.post("/process/{job_id}")
def process(job_id: str, format: str = "gif"):
    input_file = f"{INPUT_DIR}/{job_id}.mp4"

    if format == "gif":
        output_file = f"{OUTPUT_DIR}/{job_id}.gif"

        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-vf", "fps=30,scale=640:-1:flags=lanczos",
            "-loop", "0",
            output_file
        ]

    elif format == "mp4":
        output_file = f"{OUTPUT_DIR}/{job_id}.mp4"

        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-vf", "fps=30,scale=640:-1",
            "-movflags", "faststart",
            output_file
        ]

    subprocess.run(cmd)

    return {"status": "done", "download": f"/download/{job_id}?format={format}"}


@app.get("/download/{job_id}")
def download(job_id: str, format: str = "gif"):
    ext = "gif" if format == "gif" else "mp4"
    file_path = f"{OUTPUT_DIR}/{job_id}.{ext}"
    return FileResponse(file_path)
