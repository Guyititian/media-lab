from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# BALANCED INTERPOLATION ENGINE v3
# ----------------------------
def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        # 1. Preserve edge sharpness (important for logos/text)
        "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"

        # 2. Stable color boost (not overdone)
        "eq=contrast=1.08:saturation=1.22:brightness=0.01,"

        # 3. 🔥 CONTROLLED INTERPOLATION (key fix)
        # back to safer temporal density
        "minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"

        # 4. Restore higher color fidelity (important fix vs v2)
        "format=yuv444p,"

        # 5. Light denoise ONLY (protect flat backgrounds)
        "hqdn3d=1.0:1.0:3:3,"

        # 6. CLEAN palette pipeline (no aggressive dithering)
        "split[s0][s1];"
        "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
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
    return {"status": "media-lab interpolation engine v3 balanced"}


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
