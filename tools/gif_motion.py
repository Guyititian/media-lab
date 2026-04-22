import subprocess
from core.presets import get_preset


def build_filter(preset: dict) -> str:
    """
    SAFE builder:
    - supports both balanced + fluid presets
    - prevents missing key crashes
    """

    scale = preset["scale"]
    fps = preset["fps"]

    contrast = preset.get("contrast", 1.0)
    saturation = preset.get("saturation", 1.0)
    brightness = preset.get("brightness", 0.0)

    # motion interpolation (only for fluid)
    if preset.get("minterpolate", False):
        mi_filter = (
            f"minterpolate=fps={fps}:"
            f"mi_mode={preset.get('mi_mode','mci')}:"
            f"mc_mode={preset.get('mc_mode','aobmc')}:"
            f"me_mode={preset.get('me_mode','bidir')}:"
            f"vsbmc={preset.get('vsbmc',1)},"
        )
    else:
        mi_filter = f"fps={fps},"

    filter_chain = (
        f"scale={scale}:flags=lanczos:force_original_aspect_ratio=decrease,"
        f"{mi_filter}"
        f"eq=contrast={contrast}:saturation={saturation}:brightness={brightness},"
        f"format={preset.get('yuv','yuv420p')},"
        f"split[s0][s1];"
        f"[s0]palettegen=max_colors={preset.get('palette_max_colors',256)}:stats_mode={preset.get('palette_mode','diff')}[p];"
        f"[s1][p]paletteuse=dither={preset.get('dither','bayer')}"
    )

    return filter_chain


def generate_gif(input_path: str, output_path: str, preset_name: str) -> str:

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
