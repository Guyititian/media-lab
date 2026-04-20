from fastapi import FastAPI, File, UploadFile
import os
import uuid
import shutil

app = FastAPI()

# Folders
INPUT_DIR = "input"
OUTPUT_DIR = "output"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"status": "media-lab running"}

# -------------------------
# UPLOAD ENDPOINT
# -------------------------
@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    file_path = os.path.join(INPUT_DIR, f"{job_id}.mp4")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "job_id": job_id,
        "status": "uploaded"
    }

# -------------------------
# PROCESS ENDPOINT (SAFE PLACEHOLDER)
# -------------------------
@app.post("/process/{job_id}")
def process(job_id: str, format: str = "gif"):
    return {
        "status": "error",
        "message": "ffmpeg not installed yet. Processing disabled for now.",
        "job_id": job_id
    }

# -------------------------
# DOWNLOAD ENDPOINT (placeholder)
# -------------------------
@app.get("/download/{job_id}")
def download(job_id: str):
    file_path = os.path.join(INPUT_DIR, f"{job_id}.mp4")

    if not os.path.exists(file_path):
        return {"error": "file not found"}

    return {
        "status": "file exists",
        "path": file_path
    }
