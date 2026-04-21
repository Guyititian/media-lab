from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()

def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        "fps=24,"
        "scale=640:-1:flags=lanczos,"
        "split[s0][s1];"
        "[s0]palettegen[p];"
        "[s1][p]paletteuse"
    )

    result = subprocess.run([
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-loop", "0",
        output_path
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        with open(input_path, "wb") as f:
            f.write(await file.read())

        build_gif(input_path, output_path)

        with open(output_path, "rb") as f:
            gif_data = f.read()

    app.state.storage = getattr(app.state, "storage", {})
    app.state.storage[job_id] = gif_data

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
