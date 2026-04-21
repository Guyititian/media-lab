from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# GIF ENGINE (QUALITY FIXED FULL PIPELINE)
# ----------------------------
def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        # remove compression noise FIRST (fixes green/background artifacts)
        "hqdn3d=1.5:1.5:6:6,"

        # scale with high-quality resampling
        "scale=640:-1:flags=lanczos:force_original_aspect_ratio=decrease,"

        # mild normalization (prevents washed-out greens without overboosting)
        "eq=saturation=1.08:contrast=1.05:gamma=1.02,"

        # stable frame rate
        "fps=24,"

        # clean palette generation (important for flat UI backgrounds)
        "split[s0][s1];"
        "[s0]palettegen=stats_mode=single:max_colors=256:reserve_transparent=0[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,

        # FFmpeg 7 safe timing mode
        "-fps_mode", "cfr",

        "-loop", "0",
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
    return {"status": "media-lab gif engine (quality fixed build)"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        try:
            build_gif(input_path, output_path)
        except Exception as e:
            return {"job_id": job_id, "error": str(e)}

        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            return {"job_id": job_id, "error": "empty output"}

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
