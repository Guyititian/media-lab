from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# MEDIA-LAB GIF ENGINE (v6 stable)
# ----------------------------
def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        # preserve detail BEFORE compression
        "scale=640:-1:flags=lanczos:force_original_aspect_ratio=decrease,"
        
        # stable playback baseline
        "fps=24,"
        
        # palette tuned for better color retention (greens/saturation)
        "split[s0][s1];"
        "[s0]palettegen=max_colors=256:stats_mode=full:reserve_transparent=0[p];"
        "[s1][p]paletteuse=dither=floyd_steinberg:bayer_scale=1"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,

        # filter graph
        "-vf", vf,

        # normalize playback speed across devices
        "-r", "24",
        "-vsync", "0",

        # loop forever (GIF standard behavior)
        "-loop", "0",

        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ----------------------------
# API
# ----------------------------
@app.get("/")
def root():
    return {"status": "media-lab v6 stable GIF engine running"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        # save upload
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        # generate gif
        build_gif(input_path, output_path)

        # safety check
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            return {"job_id": job_id, "error": "conversion failed"}

        with open(output_path, "rb") as f:
            gif_data = f.read()

    # in-memory storage (MVP safe)
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
