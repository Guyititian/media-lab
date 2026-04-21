from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# STABLE HIGH QUALITY PIPELINE (v1.2 tuned)
# ----------------------------
def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        # 1. Clean scaling (sharp but stable)
        "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"

        # 2. Stable FPS (no interpolation changes)
        "fps=24,"

        # 3. Light denoise (preserve detail, reduce artifacts)
        "hqdn3d=0.8:0.8:3:3,"

        # 4. Proper GIF-compatible color space
        "format=yuv420p,"

        # 5. Palette pipeline (stabilized colors)
        "split[s0][s1];"
        "[s0]palettegen=max_colors=256:stats_mode=single[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-loop", "0",
        "-movflags", "+faststart",
        "-an",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ----------------------------
# API
# ----------------------------
@app.get("/")
def root():
    return {"status": "media-lab stable gif engine v1.2 tuned"}


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
