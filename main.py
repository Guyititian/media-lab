from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os

import cv2
import numpy as np

app = FastAPI()


# ----------------------------
# FAST MODE (unchanged stable baseline)
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
# EDGE-AWARE SHARPENING (SAFE MODE A)
# ----------------------------
def edge_sharpen_frame(img):
    """
    Light edge-preserving sharpening:
    - detect edges (Sobel)
    - apply gentle unsharp only where edges exist
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Edge detection (soft mask, not binary)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edge = cv2.magnitude(sobelx, sobely)

    edge = cv2.normalize(edge, None, 0, 1.0, cv2.NORM_MINMAX)

    # Gentle blur + sharpen
    blurred = cv2.GaussianBlur(img, (0, 0), 1.0)
    sharpened = cv2.addWeighted(img, 1.25, blurred, -0.25, 0)

    # Blend sharpen only on edges
    edge_3ch = cv2.merge([edge, edge, edge])
    result = img * (1 - edge_3ch) + sharpened * edge_3ch

    return np.clip(result, 0, 255).astype(np.uint8)


# ----------------------------
# AI PIPELINE (SAFE VERSION A)
# ----------------------------
def run_ai_pipeline(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.TemporaryDirectory() as tmp:

        frames_dir = os.path.join(tmp, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        processed_dir = os.path.join(tmp, "processed")
        os.makedirs(processed_dir, exist_ok=True)

        interp_video = os.path.join(tmp, "interp.mp4")

        # STEP 1: extract frames
        extract = [
            ffmpeg,
            "-y",
            "-i", input_path,
            os.path.join(frames_dir, "%04d.png")
        ]
        subprocess.run(extract, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # STEP 2: OpenCV edge-aware sharpening
        frame_files = sorted(os.listdir(frames_dir))

        for f in frame_files:
            path = os.path.join(frames_dir, f)
            img = cv2.imread(path)

            if img is None:
                continue

            processed = edge_sharpen_frame(img)

            cv2.imwrite(os.path.join(processed_dir, f), processed)

        # STEP 3: rebuild video at higher FPS
        rebuild = [
            ffmpeg,
            "-y",
            "-framerate", "60",
            "-i", os.path.join(processed_dir, "%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "16",
            interp_video
        ]
        subprocess.run(rebuild, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # STEP 4: GIF encode (UNCHANGED stability baseline)
        vf_final = (
            "format=yuv444p,"
            "hqdn3d=0.5:0.5:2:2,"
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
        run_ai_pipeline(input_path, output_path)
    else:
        build_fast_gif(input_path, output_path)


# ----------------------------
# API
# ----------------------------
@app.get("/")
def root():
    return {"status": "media-lab v8.0 safe edge-aware pipeline running"}


@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    mode: str = Query(default="fast")
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
