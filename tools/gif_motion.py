# tools/gif_motion.py

import os
import subprocess
from core.presets import get_preset


def generate_gif(input_path: str, output_path: str, preset_name: str):
    """
    Core GIF motion engine
    - resolves preset safely
    - builds deterministic ffmpeg pipeline
    """

    # -----------------------------
    # 1. Resolve preset (CRITICAL FIX)
    # -----------------------------
    preset = get_preset(preset_name)

    if not isinstance(preset, dict):
        raise TypeError("Preset must be a resolved dict")

    filter_complex = preset["filter"]
    fps = preset.get("fps", 24)

    # -----------------------------
    # 2. Build FFmpeg command
    # -----------------------------
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-filter_complex", filter_complex,
        "-r", str(fps),
        "-an",
        output_path
    ]

    # -----------------------------
    # 3. Debug logging (important for Render)
    # -----------------------------
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔥 TOOL: gif_motion")
    print(f"🔥 PRESET: {preset_name}")
    print(f"🔥 INPUT: {input_path}")
    print(f"🔥 OUTPUT: {output_path}")
    print(f"🔥 FPS: {fps}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🔥 FILTER: {filter_complex}")

    # -----------------------------
    # 4. Validate input path (fixes your dict/path bug indirectly)
    # -----------------------------
    if isinstance(input_path, dict):
        raise TypeError("Input path is dict — expected file path string")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # -----------------------------
    # 5. Execute FFmpeg
    # -----------------------------
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print("❌ FFmpeg ERROR:")
        print(result.stderr)
        raise RuntimeError("GIF generation failed")

    return output_path
