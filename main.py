from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

app = FastAPI()


# ----------------------------
# FAST MODE (baseline stable)
# ----------------------------
def build_fast_gif(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
        "eq=contrast=1.08:saturation=1.25:brightness=0.01,"
        "fps=24,"
        "format=yuv444p,"
        "hqdn3d=1.2:1.2:6:6,"
        "split[s0][s1];"
        "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
    )

    cmd = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-loop", "0",
        "-fs", "10M",
        output_path
    ]

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ----------------------------
# AI MODE (smooth + sharpened)
# ----------------------------
def run_ai_interpolation(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.TemporaryDirectory() as tmp:

        frames_dir = os.path.join(tmp, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        interp_video = os.path.join(tmp, "interp.mp4")

        # STEP 1: extract frames
        extract = [
            ffmpeg,
            "-y",
            "-i", input_path,
            os.path.join(frames_dir, "%04d.png")
        ]
        subprocess.run(extract, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # STEP 2: AI interpolation placeholder (RIFE hook)
        interp_dir = frames_dir

        # STEP 3: rebuild HIGH FPS intermediate video
        rebuild = [
            ffmpeg,
            "-y",
            "-framerate", "60",
            "-i", os.path.join(interp_dir, "%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "16",
            interp_video
        ]
        subprocess.run(rebuild, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # STEP 4: FINAL GIF ENCODE
        vf_final = (
            "format=yuv444p,"
            "hqdn3d=0.5:0.5:2:2,"
            "unsharp=lx=7:ly=7:la=1.2,"
            "eq=contrast=1.06:saturation=1.22:brightness=0.01,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=single[p];"
            "[s1][p]paletteuse=dither=floyd_steinberg"
        )

        final_cmd = [
            ffmpeg,
            "-y",
            "-i", interp_video,
            "-vf", vf_final,
            "-loop", "0",
            "-fs", "12M",
            output_path
        ]

        subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ----------------------------
# ROUTER
# ----------------------------
def build_gif(mode, input_path, output_path):
    if mode == "ai":
        run_ai_interpolation(input_path, output_path)
    else:
        build_fast_gif(input_path, output_path)


# ----------------------------
# API
# ----------------------------
@app.get("/")
def root():
    return {"status": "media-lab v7.2 stronger sharpening GIF engine running"}


@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    mode: str = Query(default="fast")  # fast | ai
):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        build_gif(mode, input_path, output_path)

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {"job_id": job_id, "error": "conversion failed"}

        with open(output_path, "rb") as f:
            gif_data = f.read()

    app.state.storage = getattr(app.state, "storage", {})
    app.state.storage[job_id] = gif_data

    return {
        "job_id": job_id,
        "mode": mode,
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
