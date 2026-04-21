import subprocess
import imageio_ffmpeg


def process(input_path: str, output_path: str):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    vf = (
        # sharp scaling
        "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
        
        # color enhancement (your proven good baseline)
        "eq=contrast=1.08:saturation=1.25:brightness=0.01,"
        
        # stable FPS (no interpolation yet)
        "fps=24,"
        
        # better color precision before palette
        "format=yuv444p,"
        
        # light denoise to reduce banding
        "hqdn3d=1.2:1.2:6:6,"
        
        # palette pipeline (stable)
        "split[s0][s1];"
        "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
    )

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-loop", "0",
        "-fs", "10M",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
