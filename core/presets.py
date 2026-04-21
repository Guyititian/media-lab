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

    "fluid_motion_v1": {
        "label": "Fluid Motion (Palette Optimized)",
        "description": "Improved color stability and sharper perceived edges with optimized palette generation.",
        "vf": (
            # stable geometry (no change)
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"

            # keep your proven sharpness + color base
            "unsharp=5:5:1.0:3:3:0.5,"
            "eq=contrast=1.12:saturation=1.35:brightness=0.01,"

            # locked motion (correct decision you made)
            "minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,"

            # color preservation baseline
            "format=yuv444p,"

            # lighter denoise to avoid “muddying” edges
            "hqdn3d=0.7:0.7:2:2,"

            # 🔥 KEY CHANGE: better palette generation strategy
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=single:reserve_transparent=0:stats_mode=diff[p];"

            # 🔥 KEY CHANGE: improved dithering behavior (less shimmer)
            "[s1][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle:bayer_scale=0"
        )
    }
}
