from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import uuid
import subprocess
import imageio_ffmpeg
import tempfile
import os
import cv2

app = FastAPI()


# ----------------------------
# STAGE 2: OpenCV enhancement
# ----------------------------
def enhance_frames(input_path):
    cap = cv2.VideoCapture(input_path)

    frames = []
    fps = cap.get(cv2.CAP_PROP_FPS)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # light enhancement only (NO artifact amplification)
        frame = cv2.convertScaleAbs(frame, alpha=1.08, beta=2)

        frames.append(frame)

    cap.release()
    return frames, fps


# ----------------------------
# STAGE 3+4: Encode GIF via FFmpeg pipe
# ----------------------------
def encode_gif(frames, fps, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.TemporaryDirectory() as tmp:
        frame_pattern = os.path.join(tmp, "frame_%04d.png")

        for i, frame in enumerate(frames):
            cv2.imwrite(frame_pattern % i, frame)

        vf = (
            "fps=24,"
            "scale=640:-1:flags=lanczos:force_original_aspect_ratio=decrease,"
            "split[s0][s1];"
            "[s0]palettegen[p];"
            "[s1][p]paletteuse=dither=floyd_steinberg"
        )

        cmd = [
            ffmpeg,
            "-y",
            "-framerate", "24",
            "-i", os.path.join(tmp, "frame_%04d.png"),
            "-vf", vf,
            "-loop", "0",
            "-f", "gif",
            output_path
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ----------------------------
# API
# ----------------------------
@app.get("/")
def root():
    return {"status": "media-lab pipeline v1 running"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        input_path = os.path.join(tmp, "input.mp4")
        output_path = os.path.join(tmp, "output.gif")

        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        # STAGE 2
        frames, fps = enhance_frames(input_path)

        # STAGE 3 + 4
        encode_gif(frames, fps, output_path)

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
