from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# CORE ENGINE (v1 QUALITY PIPELINE)
# ----------------------------
def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,

        # ----------------------------
        # 🎯 QUALITY LAYER (this is your differentiator)
        # ----------------------------
        "-vf",
        (
            "fps=24,"
            "scale=540:-1:flags=lanczos,"
            "minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=5"
        ),

        "-loop", "0",
        "-fs", "8M",  # soft cap for Nuvio-safe behavior
        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ----------------------------
# API
# ----------------------------
@app.get("/")
def root():
    return {"status": "media-lab v1 running"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.TemporaryDirectory() as tmp:

        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        # Save upload
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        # Run enhancement engine
        build_gif(input_path, output_path)

        # Read result into memory (safe from Render disk resets)
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {
                "job_id": job_id,
                "error": "conversion failed"
            }

        with open(output_path, "rb") as f:
            gif_data = f.read()

    # store in-memory (MVP safe)
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
