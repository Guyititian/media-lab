import os
import uuid
import subprocess

from core.presets import get_preset, PRESETS

OUTPUT_DIR = "outputs"
UPLOAD_DIR = "uploads"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


def generate_gif(input_path: str, preset_name: str):
    """
    Generate GIF using resolved preset filter string.
    """

    preset = get_preset(preset_name)

    if "filter" not in preset:
        raise ValueError(f"Preset '{preset_name}' missing filter key")

    filter_chain = preset["filter"]

    output_name = f"{uuid.uuid4()}.gif"
    output_path = os.path.join(OUTPUT_DIR, output_name)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔥 GIF MOTION ENGINE")
    print(f"🔥 INPUT: {input_path}")
    print(f"🔥 PRESET: {preset_name}")
    print("🔥 FILTER PIPELINE:")
    print(filter_chain)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", filter_chain,
        "-loop", "0",
        output_path
    ]

    subprocess.run(cmd, check=True)

    return f"/outputs/{output_name}"


# IMPORTANT: expose PRESETS if routes still imports it anywhere
# (prevents accidental import crashes during deploy overlap)
