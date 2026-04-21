from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# QUALITY ENGINE v4 (GIF-first)
# ----------------------------
def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        # ----------------------------
        # 1. mild perceptual correction (NOT heavy grading)
        # ----------------------------
        "eq=contrast=1.05:saturation=1.08:brightness=0.01,"
        
        # ----------------------------
        # 2. clean scaling (avoid aliasing noise)
        # ----------------------------
        "scale=640:-1:flags=lanczos:force_original_aspect_ratio=decrease,"
        
        # ----------------------------
        # 3. FPS normalization (stable, no interpolation conflicts)
        # ----------------------------
        "fps=24,"
        
        # ----------------------------
        # 4. split pipeline for better palette sampling
        # ----------------------------
        "split[s0][s1];"
        
        # ----------------------------
        # 5. palette generation (key improvement)
        #    - stats_mode=single reduces noise sensitivity
        #    - slight pre-denoise improves flat colors
        # ----------------------------
        "[s0]hqdn3d=1.2:1.2:6:6,palettegen=max_colors=256:stats_mode=single[p];"
        
        # ----------------------------
        # 6. apply palette (controlled dithering)
        # ----------------------------
        "[s1][p]paletteuse=dither=floyd_steinberg:diff_mode=rectangle"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-loop", "0",
        "-fs", "8M",
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
    return {"status": "media-lab v4 GIF quality engine running"}


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
