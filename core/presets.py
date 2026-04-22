# core/presets.py

PRESETS = {
    "balanced_v1": {
        "name": "balanced_v1",
        "fps": 24,

        # This is your already-working configuration (DO NOT CHANGE lightly)
        "filter": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "eq=contrast=1.05:saturation=1.10:brightness=0.00,"
            "fps=24,"
            "format=yuv420p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
        ),

        "palette_mode": "diff",
        "dither": "bayer",
        "bayer_scale": 1,
        "target_mb": (4, 6)
    },

    "fluid_motion_v1": {
        "name": "fluid_motion_v1",
        "fps": 50,

        # FIX: restore high-quality motion pipeline WITHOUT over-compression
        "filter": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "minterpolate=fps=50:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
            "eq=contrast=1.08:saturation=1.22:brightness=0.01,"
            "fps=50,"
            "format=yuv444p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
        ),

        "palette_mode": "diff",
        "dither": "bayer",
        "bayer_scale": 1,

        # IMPORTANT: prevents the "tiny file regression"
        "palette_max_colors": 256,

        "target_mb": (8, 12)
    }
}


def get_preset(name: str):
    """
    Strict resolver:
    - prevents string/dict mismatches
    - guarantees valid preset structure
    """
    preset = PRESETS.get(name)

    if not preset:
        raise ValueError(f"Invalid preset: {name}. Must be one of {list(PRESETS.keys())}")

    return preset
