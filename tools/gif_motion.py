# tools/gif_motion.py

import subprocess
import uuid
import os
from core.presets import get_preset

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_gif(input_path: str, preset_name: str):
    preset = get_preset(preset_name)

    output_name = f"{uuid.uuid4()}.gif"
    output_path = os.path.join(OUTPUT_DIR, output_name)

    # ------------------------------------------------------------
    # SAFETY LAYER: prevent Render timeout / runaway ffmpeg
    # ------------------------------------------------------------

    # Force lightweight GIF-friendly constraints at runtime
    base_filter = preset["filter"]

    # Ensure stable fps + scaling safety without altering preset system
    safe_filter = f"{base_filter},fps=24,scale=720:-1:flags=lanczos"

    cmd = [
        "ffmpeg",
        "-y",

        # input
        "-i", input_path,

        # safety-limited filter chain
        "-vf", safe_filter,

        # reduce GIF memory explosion
        "-gifflags", "+transdiff",
        "-pix_fmt", "rgb24",

        # loop forever (GIF standard behavior)
        "-loop", "0",

        output_path
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            timeout=120  # prevents Render hard kill / 502
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError("GIF generation timed out (preset too heavy for server limits)")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {str(e)}")

    return {
        "output_path": output_path,
        "output_url": f"/outputs/{output_name}"
    }
