import subprocess
import os
import uuid
from core.presets import PRESETS


def generate_gif(input_path: str, preset_key: str, output_dir: str = "outputs") -> str:
    os.makedirs(output_dir, exist_ok=True)

    preset = PRESETS.get(preset_key, PRESETS["balanced_v1"])
    vf = preset["vf"]

    output_path = os.path.join(output_dir, f"{uuid.uuid4()}.gif")

    print("🔥 USING PRESET:", preset_key)
    print("🔥 FILTER STRING:", vf)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-an",
        output_path
    ]

    subprocess.run(cmd, check=True)

    return output_path
