def run_ai_interpolation(input_path, output_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.TemporaryDirectory() as tmp:
        interp_video = os.path.join(tmp, "interp.mp4")

        # STEP 1: AI interpolation (your existing stage)
        frames_dir = os.path.join(tmp, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        extract = [
            ffmpeg,
            "-y",
            "-i", input_path,
            os.path.join(frames_dir, "%04d.png")
        ]
        subprocess.run(extract, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # (RIFE step assumed here — even if external)
        interp_dir = frames_dir

        # STEP 2: rebuild HIGH-FPS intermediate video (IMPORTANT CHANGE)
        rebuild = [
            ffmpeg,
            "-y",
            "-framerate", "60",
            "-i", os.path.join(interp_dir, "%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "16",
            interp_video
        ]
        subprocess.run(rebuild, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # STEP 3: GIF encode tuned for smooth motion preservation
        vf_final = (
            # preserve gradients better before palette
            "format=yuv444p,"

            # very light denoise ONLY (important: don't overdo it)
            "hqdn3d=0.6:0.6:2:2,"

            # color stability
            "eq=contrast=1.05:saturation=1.20:brightness=0.01,"

            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=single[p];"
            "[s1][p]paletteuse=dither=floyd_steinberg"
        )

        final_cmd = [
            ffmpeg,
            "-y",
            "-i", interp_video,
            "-vf", vf_final,
            "-loop", "0",
            "-fs", "12M",
            output_path
        ]

        subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
