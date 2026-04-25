import os
import subprocess
import uuid

from core.config import OUTPUT_DIR, FFMPEG_TIMEOUT_SECONDS
from core.presets import get_preset


def generate_gif(input_path: str, preset_name: str):
    preset = get_preset(preset_name)

    output_name = f"{uuid.uuid4()}.gif"
    output_path = os.path.join(OUTPUT_DIR, output_name)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", input_path,
        "-vf", preset["vf"],
        "-loop", "0",
        output_path
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            timeout=FFMPEG_TIMEOUT_SECONDS,
            capture_output=True,
            text=True
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Processing timed out. Try a shorter clip, smaller file, or lighter preset."
        )

    except subprocess.CalledProcessError as error:
        ffmpeg_error = error.stderr.strip() if error.stderr else "Unknown FFmpeg error."
        raise RuntimeError(f"FFmpeg failed: {ffmpeg_error}")

    if not os.path.exists(output_path):
        raise RuntimeError("Processing failed: output file was not created.")

    return {
        "output_path": output_path,
        "output_url": f"/outputs/{output_name}"
    }
