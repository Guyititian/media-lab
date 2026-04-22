import subprocess
import uuid
import os

OUTPUT_DIR = "outputs"

# ----------------------------------
# PRESETS (FINAL TUNED VERSIONS)
# ----------------------------------
PRESETS = {

    # FAST / CLEAN / SMALLER FILE
    "balanced_v1": {
        "filter": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "fps=24,"
            "eq=contrast=1.04:saturation=1.08:brightness=0.01,"
            "format=yuv444p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
        )
    },

    # HIGH-END / 50 FPS / SMOOTH MOTION
    "fluid_motion_v1": {
        "filter": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "minterpolate=fps=50:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,"
            "eq=contrast=1.05:saturation=1.15:brightness=0.01,"
            "format=yuv444p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=single[p];"
            "[s1][p]paletteuse=dither=floyd_steinberg"
        )
    }
}


# ----------------------------------
# MAIN ENGINE
# ----------------------------------
def generate_gif(input_path: str, preset: dict) -> str:
    if not isinstance(preset, dict):
        raise Exception("Preset must be resolved dict")

    filter_str = preset["filter"]

    output_filename = f"{uuid.uuid4()}.gif"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔥 GIF MOTION ENGINE")
    print(f"🔥 INPUT: {input_path}")
    print(f"🔥 FILTER PIPELINE:\n{filter_str}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", filter_str,
        "-gifflags", "-offsetting",
        "-loglevel", "error",
        output_path
    ]

    subprocess.run(cmd, check=True)

    return f"/outputs/{output_filename}"
