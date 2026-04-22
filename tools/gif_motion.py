import subprocess
from core.presets import get_preset


def build_filter(preset: dict) -> str:
    """
    Build ffmpeg filter chain from preset dict
    """

    return (
        f"scale={preset['scale']}:flags=lanczos:force_original_aspect_ratio=decrease,"
        f"minterpolate=fps={preset['fps']}:mi_mode=mci:mc_mode={preset['mc_mode']}:me_mode=bidir,"
        f"eq=contrast={preset['contrast']}:saturation={preset['saturation']}:brightness={preset['brightness']},"
        f"format=yuv444p,"
        f"split[s0][s1];"
        f"[s0]palettegen=max_colors={preset['max_colors']}:stats_mode=single[p];"
        f"[s1][p]paletteuse=dither={preset['dither']}"
    )


def generate_gif(input_path: str, output_path: str, preset_name: str) -> str:
    """
    Main GIF generator
    """

    preset = get_preset(preset_name)

    filter_chain = build_filter(preset)

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
        "-r", str(preset["fps"]),
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        raise Exception("FFmpeg processing failed")

    return output_path
