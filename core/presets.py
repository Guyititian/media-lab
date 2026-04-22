# core/presets.py

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
        "label": "Fluid Motion (Optimized)",
        "description": "Balanced smoothness with improved sharpness and vivid color.",
        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "unsharp=5:5:1.0:3:3:0.5,"
            "eq=contrast=1.12:saturation=1.35:brightness=0.01,"
            "minterpolate=fps=36:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,"
            "format=yuv444p,"
            "hqdn3d=0.8:0.8:2:2,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=2"
        )
    }
}


# ✅ ADD THIS (THIS FIXES YOUR CRASH)
def get_preset(name: str):
    preset = PRESETS.get(name)
    if not preset:
        raise ValueError(f"Invalid preset: {name}")
    return preset
