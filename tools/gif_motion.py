import os
import uuid
import subprocess

OUTPUT_DIR = "outputs"
UPLOAD_DIR = "uploads"


# -----------------------------
# PRESET DEFINITIONS (SOURCE OF TRUTH)
# -----------------------------
PRESETS = {
    "balanced_v1": {
        "fps": 24,
        "scale": 720,
        "motion": "basic",
        "palette_colors": 128,
        "speed": 1.0,
    },
    "fluid_motion_v1": {
        "fps": 60,
        "scale": 720,
        "motion": "advanced",
        "palette_colors": 256,
        "speed": 0.75,
    },
}


# -----------------------------
# MAIN ENTRY
# -----------------------------
def generate_gif(input_path: str, preset: dict) -> str:
    """
    Returns: output_url (relative path like /outputs/file.gif)
    """

    if isinstance(preset, str):
        raise TypeError("Preset must be resolved dict, not string")

    fps = preset["fps"]
    scale = preset["scale"]
    palette_colors = preset["palette_colors"]
    speed = preset["speed"]
    motion = preset["motion"]

    output_filename = f"{uuid.uuid4()}.gif"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # -----------------------------
    # PIPELINE DESIGN (FIXED ORDER)
    # -----------------------------
    if motion == "basic":
        vf = (
            f"scale={scale}:-2:flags=lanczos,"
            f"fps={fps},"
            f"format=rgb24"
        )

    elif motion == "advanced":
        vf = (
            f"scale={scale}:-2:flags=lanczos,"
            f"minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
            f"setpts={speed}*PTS,"
            f"format=rgb24"
        )

    else:
        raise ValueError(f"Unknown motion mode: {motion}")

    # -----------------------------
    # TWO PASS GIF PIPELINE (STABLE)
    # -----------------------------

    palette_path = os.path.join(OUTPUT_DIR, f"palette_{uuid.uuid4()}.png")

    # PASS 1: generate palette
    palette_cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", vf + f",palettegen=max_colors={palette_colors}:stats_mode=diff",
        palette_path
    ]

    # PASS 2: generate gif using palette
    gif_cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-i", palette_path,
        "-filter_complex",
        f"{vf}[x];[x][1:v]paletteuse=dither=floyd_steinberg",
        output_path
    ]

    try:
        subprocess.run(palette_cmd, check=True, capture_output=True)
        subprocess.run(gif_cmd, check=True, capture_output=True)

    finally:
        # cleanup palette
        if os.path.exists(palette_path):
            os.remove(palette_path)

    return f"/outputs/{output_filename}"
