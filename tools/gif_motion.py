# tools/gif_motion.py

import subprocess
import uuid
from core.presets import PRESETS, get_preset


def generate_gif(input_path: str, preset_name: str):
    preset = get_preset(preset_name)

    output_id = str(uuid.uuid4())
    output_path = f"outputs/{output_id}.gif"

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", preset["filter"],
        "-r", str(preset["fps"]),
        "-loop", "0",
        output_path
    ]

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔥 GIF MOTION ENGINE")
    print(f"🔥 INPUT: {input_path}")
    print(f"🔥 PRESET: {preset_name}")
    print("🔥 FILTER PIPELINE:")
    print(preset["filter"])
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

    subprocess.run(ffmpeg_cmd, check=True)

    return output_path


# REQUIRED FOR ROUTES IMPORT (fixes your crash)
PRESETS = PRESETS
