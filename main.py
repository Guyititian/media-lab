from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# GIF ENGINE v5.3 (STABILITY FIRST)
# ----------------------------
def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        # ----------------------------
        # mild normalization (reduces color instability)
        # ----------------------------
        "eq=contrast=1.05:saturation=1.08:brightness=0.01,"

        # ----------------------------
        # clean scaling (no artifacts introduced)
        # ----------------------------
        "scale=640:-1:flags=lanczos:force_original_aspect_ratio=decrease,"

        # ----------------------------
        # stable frame timing
        # ----------------------------
        "fps=24,"

        # ----------------------------
        # palette generation (STABLE MODE - avoids frame-to-frame drift)
        # ----------------------------
        "split[s0][s1];"
        "[s0]palettegen=max_colors=256:stats_mode=single:reserve_transparent=0[p];"

        # ----------------------------
        # IMPORTANT CHANGE:
        # remove noisy dithering completely
        # ----------------------------
        "[s1][p]paletteuse=dither=none"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-loop", "0",
        "-f", "gif",
        output_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)


# ----------------------------
# API
# ----------------------------
@app.get("/")
def root():
    return {"status": "media-lab v5.3 stability GIF engine running"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        build_gif(input_path, output_path)

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {"job_id": job_id, "error": "conversion failed"}

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
