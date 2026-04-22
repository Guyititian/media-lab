# core/presets.py

PRESETS = {

    # -------------------------------------------------
    # ✅ STABLE BASELINE (DO NOT CHANGE VISUALLY)
    # -------------------------------------------------
    "balanced_v1": {
        "name": "balanced_v1",
        "fps": 24,

        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "eq=contrast=1.05:saturation=1.10:brightness=0.00,"
            "fps=24,"
            "format=yuv420p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
        ),

        "palette": {
            "mode": "diff",
            "max_colors": 256,
            "dither": "bayer",
            "bayer_scale": 1
        },

        "target_mb": (4, 6)
    },

    # -------------------------------------------------
    # 🚀 HIGH QUALITY FLUID MOTION (RESTORED VERSION)
    # -------------------------------------------------
    "fluid_motion_v1": {
        "name": "fluid_motion_v1",
        "fps": 50,

        # This is your previously successful “reddit-quality” pipeline
        "vf": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "unsharp=5:5:1.0:3:3:0.5,"
            "eq=contrast=1.12:saturation=1.28:brightness=0.01,"
            "minterpolate=fps=50:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
            "format=yuv444p,"
            "hqdn3d=0.9:0.9:2:2,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff:reserve_transparent=0[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
        ),

        "palette": {
            "mode": "diff",
            "max_colors": 256,
            "dither": "bayer",
            "bayer_scale": 1
        },

        "target_mb": (8, 14)
    }
}


def get_preset(name: str):
    """
    Strict preset resolver:
    - guarantees valid preset exists
    - prevents partial dict/string mismatches
    """
    preset = PRESETS.get(name)

    if not preset:
        raise ValueError(
            f"Invalid preset: {name}. Must be one of {list(PRESETS.keys())}"
        )

    return preset
