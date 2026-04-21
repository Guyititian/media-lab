PRESETS = {
    "balanced_v1": {
        "label": "Balanced",
        "description": "Stable output with clean colors and minimal artifacts.",
        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "eq=contrast=1.08:saturation=1.22:brightness=0.01,"
            "fps=24,"
            "format=yuv444p,"
            "hqdn3d=1.0:1.0:3:3,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
        )
    },

    # 🟢 SAFE HIGH QUALITY (what Render can handle)
    "fluid_motion_v1": {
        "label": "Fluid Motion (Safe)",
        "description": "Smooth motion with good color, optimized for stability.",
        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "eq=contrast=1.10:saturation=1.25:brightness=0.01,"
            "minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,"
            "format=yuv420p,"
            "hqdn3d=1.0:1.0:3:3,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
        )
    },

    # 🔥 FULL QUALITY MODE (your original “best output target”)
    "fluid_motion_heavy": {
        "label": "Fluid Motion (High Quality)",
        "description": "Maximum smoothness and color fidelity. May be memory intensive.",
        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "eq=contrast=1.12:saturation=1.30:brightness=0.01,"
            "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
            "format=yuv444p,"
            "hqdn3d=1.0:1.0:4:4,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=2:diff_mode=rectangle"
        )
    }
}
