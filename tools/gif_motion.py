import imageio_ffmpeg
import subprocess

def build_gif(input_path, output_path, vf):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    print("🔥 APPLYING VF:", vf[:120], "...")  # DEBUG (important)

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
