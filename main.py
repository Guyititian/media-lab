from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import os

app = FastAPI()

# single stable output directory (CRITICAL FIX)
BASE_DIR = "/tmp/media_lab"
os.makedirs(BASE_DIR, exist_ok=True)


def build_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        "hqdn3d=1.5:1.5:6:6,"
        "scale=640:-1:flags=lanczos:force_original_aspect_ratio=decrease,"
        "eq=saturation=1.08:contrast=1.05:gamma=1.02,"
        "fps=24,"
        "split[s0][s1];"
        "[s0]palettegen=stats_mode=single:max_colors=256[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
    )

    result = subprocess.run([
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-fps_mode", "cfr",
        "-loop", "0",
        output_path
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)


@app.get("/")
def root():
    return {"status": "media-lab stable fixed storage pipeline"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    input_path = os.path.join(BASE_DIR, f"{job_id}.mp4")
    output_path = os.path.join(BASE_DIR, f"{job_id}.gif")

    contents = await file.read()

    with open(input_path, "wb") as f:
        f.write(contents)

    try:
        build_gif(input_path, output_path)
    except Exception as e:
        return {"job_id": job_id, "error": str(e)}

    if not os.path.exists(output_path):
        return {"job_id": job_id, "error": "no output file"}

    if os.path.getsize(output_path) < 50000:
        return {"job_id": job_id, "error": "output too small (likely failed encoding)"}

    return {
        "job_id": job_id,
        "download_url": f"/download/{job_id}"
    }


@app.get("/download/{job_id}")
def download(job_id: str):
    path = os.path.join(BASE_DIR, f"{job_id}.gif")

    if not os.path.exists(path):
        return {"error": "file not ready"}

    return FileResponse(path, media_type="image/gif", filename="output.gif")
