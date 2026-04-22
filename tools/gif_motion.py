import os
import uuid
import subprocess

# =========================================================
# PRESET SYSTEM (STRICT + FULL PIPELINES)
# =========================================================

PRESETS = {

    # -------------------------
    # BALANCED (STABLE / SMALL)
    # -------------------------
    "balanced_v1": {
        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "eq=contrast=1.05:saturation=1.15:brightness=0.0,"
            "fps=24,"
            "format=yuv420p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=3"
        )
    },

    # -------------------------
    # FLUID MOTION (HIGH QUALITY)
    # -------------------------
    "fluid_motion_v1": {
        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "minterpolate=fps=60:mi_mode=mci:mc_mode=obmc:vsbmc=1:me_mode=bidir,"
            "tblend=all_mode=average,"
            "setpts=0.75*PTS,"
            "format=yuv444p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=128:stats_mode=single[p];"
            "[s1][p]paletteuse=dither=floyd_steinberg"
        )
    }
}


# =========================================================
# BACKWARD-COMPATIBLE ENTRY POINT (FIXES IMPORT CRASH)
# =========================================================

def generate_gif(input_path: str, preset: str, output_dir: str = "outputs"):
    """
    This is the ONLY function your API should call.
    Fixes previous ImportError AND enforces preset isolation.
    """

    # -------------------------
    # VALIDATION (NO SILENT FALLBACK BLENDING)
    # -------------------------
    if preset not in PRESETS:
        raise ValueError(f"Invalid preset: {preset}. Must be one of {list(PRESETS.keys())}")

    vf = PRESETS[preset]["vf"]

    # -------------------------
    # OUTPUT SETUP
    # -------------------------
    os.makedirs(output_dir, exist_ok=True)

    output_file = f"{uuid.uuid4()}.gif"
    output_path = os.path.join(output_dir, output_file)

    # -------------------------
    # DEBUG LOGGING (IMPORTANT FOR YOU)
    # -------------------------
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔥 GIF MOTION ENGINE")
    print("🔥 INPUT:", input_path)
    print("🔥 PRESET:", preset)
    print("🔥 FILTER PIPELINE:")
    print(vf)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # -------------------------
    # FFMPEG EXECUTION
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

    return {
        "output_url": f"/outputs/{output_file}"
    }
