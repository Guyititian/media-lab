import subprocess
import imageio_ffmpeg


def process(input_path: str, output_path: str):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    # 🔒 LOCKED QUALITY PIPELINE (restores your best-known state behavior)
    vf = (
        "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
        "fps=24,"
        "format=yuv444p,"
        "eq=contrast=1.08:saturation=1.25:brightness=0.01,"
        "hqdn3d=1.2:1.2:6:6,"
        "split[s0][s1];"
        "[s0]palettegen=max_colors=256:stats_mode=diff:reserve_transparent=0[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=2:diff_mode=rectangle"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,

        # 🔒 critical stability flags (restore previous behavior consistency)
        "-loop", "0",
        "-an",
        "-vsync", "0",

        # keep cap but don't interfere with encoding behavior
        "-fs", "10M",

        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
