from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


@app.get("/")
def root():
    return {"status": "media-lab running"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    # 🔥 IMPORTANT: use true temp directory (Render-safe)
    with tempfile.TemporaryDirectory() as tmp:

        input_path = os.path.join(tmp, "input.mp4")
        palette_path = os.path.join(tmp, "palette.png")
        output_path = os.path.join(tmp, "output.gif")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        # palette step
        subprocess.run([
            ffmpeg,
            "-y",
            "-i",
            input_path,
            "-vf",
            "fps=15,scale=480:-1:flags=lanczos,palettegen",
            palette_path
        ])

        # gif step
        subprocess.run([
            ffmpeg,
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

        # 🔥 read file into memory before temp folder disappears
        with open(output_path, "rb") as f:
            gif_bytes = f.read()

    # store in global memory (safe for small MVP testing)
    app.state.storage = getattr(app.state, "storage", {})
    app.state.storage[job_id] = gif_bytes

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}"
    }


@app.get("/download/{job_id}")
def download(job_id: str):
    storage = getattr(app.state, "storage", {})

    if job_id not in storage:
        return {"error": "file not ready"}

    path = f"/tmp/{job_id}.gif"

    with open(path, "wb") as f:
        f.write(storage[job_id])

    return FileResponse(path, media_type="image/gif", filename="output.gif")
