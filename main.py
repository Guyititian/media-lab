from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# STABLE + ENHANCED GIF ENGINE
# ----------------------------
def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        # high-quality scaling with sharp preservation
        "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"

        # color enhancement BEFORE quantization (critical improvement)
        "eq=contrast=1.08:saturation=1.25:brightness=0.01,"

        # stable frame rate baseline (no interpolation yet)
        "fps=24,"

        # improves color depth before palette compression
        "format=yuv444p,"

        # mild denoise to reduce flat-area banding/artifacts
        "hqdn3d=1.2:1.2:6:6,"

        # GIF palette generation + dithering control
        "split[s0][s1];"
        "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,

        # IMPORTANT: avoid conflicting FPS flags (fixes your earlier crashes)
        "-vf", vf,
        "-loop", "0",

        # safety cap for huge outputs
        "-fs", "10M",

        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ----------------------------
# API
# ----------------------------
@app.get("/")
def root():
    return {"status": "media-lab v4 stable + color enhancement running"}


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

        # validate output
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {"job_id": job_id, "error": "conversion failed"}

        with open(output_path, "rb") as f:
            gif_data = f.read()

    # in-memory storage (simple + Render-safe)
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
