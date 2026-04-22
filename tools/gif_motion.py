import subprocess
import os
import uuid

# =========================
# PRESET DEFINITIONS (SOURCE OF TRUTH)
# =========================

PRESETS = {
    "balanced_v1": {
        "fps": 24,
        "scale": 720,
        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "eq=contrast=1.08:saturation=1.22:brightness=0.01,"
            "fps=24,"
            "format=yuv444p,"
            "split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
        )
    },

    # 🔥 TRUE FLUID MOTION PROFILE (DO NOT REDUCE TO 24fps LOOK)
    "fluid_motion_v1": {
        "fps": 48,
        "scale": 720,
        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "eq=contrast=1.12:saturation=1.28:brightness=0.02,"
            "minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
            "format=yuv444p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
        )
    }
}


# =========================
# MAIN PROCESSING FUNCTION
# =========================

def run_gif_motion(input_path: str, preset: str, output_dir: str = "outputs"):
    """
    Converts video → GIF using strict preset isolation.
    NO POST-MUTATION OF FILTERS ALLOWED.
    """

    # -------------------------
    # SAFE PRESET RESOLUTION
    # -------------------------
    if preset not in PRESETS:
        print("⚠️ Unknown preset, falling back to balanced_v1")
        preset = "balanced_v1"

    config = PRESETS[preset]

    vf = config["vf"]

    # -------------------------
    # LOCKED OUTPUT NAME
    # -------------------------
    output_name = f"{uuid.uuid4()}.gif"
    output_path = os.path.join(output_dir, output_name)

    os.makedirs(output_dir, exist_ok=True)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔥 TOOL: gif_motion")
    print(f"🔥 RAW PRESET: {preset}")
    print(f"🔥 LOCKED PRESET FPS: {config['fps']}")
    print("🔥 FILTER STRING:")
    print(vf)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # -------------------------
    # FFmpeg EXECUTION
    # -------------------------
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-loop", "0",
        output_path
    ]

    subprocess.run(cmd, check=True)

    print("✅ OUTPUT CREATED:", output_path)

    return output_path
