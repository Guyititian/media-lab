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

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,

        # IMPORTANT FIX: use "vf", not "filter"
        "-vf", preset["vf"],

        "-loop", "0",
        output_path
    ]

    subprocess.run(cmd, check=True)

    return {
        "output_path": output_path,
        "output_url": f"/outputs/{output_name}"
    }
