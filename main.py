from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# BALANCED GIF ENGINE v5
# ----------------------------
def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        # sharper scaling, but slightly less aggressive than v4
        "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"

        # selective contrast (protects shadows/highlights better than eq)
        "curves=preset=medium_contrast,"

        # mild saturation boost (reduced to prevent flat-area artifacts)
        "eq=saturation=1.15:brightness=0.01,"

        # stabilize motion perception
        "fps=24,"

        # preserve better gradients before quantization
        "format=yuv420p,"

        # reduce banding while avoiding over-dithering
        "hqdn3d=1.0:1.0:4:4,"

        # palette system tuned for stability over intensity
        "split[s0][s1];"
        "[s0]palettegen=max_colors=256:stats_mode=diff:reserve_transparent=0[p];"
        "[s1][p]paletteuse=dither=floyd_steinberg:bayer_scale=1"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-loop", "0",
        "-fs", "10M",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ----------------------------
# API
# ----------------------------
@app.get("/")
def root():
    return {"status": "media-lab v5 balanced engine running"}


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
