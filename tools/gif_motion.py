import subprocess
import imageio_ffmpeg
from core.presets import PRESETS


def process(input_path: str, output_path: str, preset: str = "balanced_v1"):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    config = PRESETS[preset]
    vf = config["vf"]

    command = [
        ffmpeg,
        "-y",
        "-i", input_path,
        "-vf", vf,
        "-loop", "0",
        "-an",
        "-vsync", "0",
        "-f", "gif",
        output_path
    ]

    subprocess.run(command)
