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
        "label": "Fluid Motion (Stabilized Sharp)",
        "description": "Sharp edges with controlled color and reduced background artifacts.",
        "vf": (
            # stable scaling
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"

            # keep the sharpness gain (this was good)
            "unsharp=5:5:1.0:3:3:0.5,"

            # slightly reduced saturation to prevent palette overflow artifacts
            "eq=contrast=1.12:saturation=1.28:brightness=0.01,"

            # keep correct motion ceiling
            "minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,"

            # preserve color depth
            "format=yuv444p,"

            # gentle denoise to reduce background instability
            "hqdn3d=0.9:0.9:2:2,"

            # 🔥 FIX: back to stable palette generation
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff:reserve_transparent=0[p];"

            # 🔥 FIX: return to Bayer (more stable, less artifacting)
            "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
        )
    }
}
