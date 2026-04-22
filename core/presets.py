# core/presets.py

PRESETS = {
    "balanced_v1": {
        "name": "balanced_v1",
        "fps": 24,
        "filter": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "fps=24,"
            "eq=contrast=1.05:saturation=1.10:brightness=0.00,"
            "format=yuv420p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
        ),
        "target_mb": (4, 6)
    },

    "fluid_motion_v1": {
        "name": "fluid_motion_v1",
        "fps": 50,

        # RESTORED EXACT WORKING QUALITY BASELINE (NO DITHER CHANGE)
        "filter": (
            "scale=720:-2:flags=lanczos:force_original_aspect_ratio=decrease,"
            "minterpolate=fps=50:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
            "eq=contrast=1.08:saturation=1.22:brightness=0.01,"
            "format=yuv444p,"
            "split[s0][s1];"
            "[s0]palettegen=max_colors=256:stats_mode=diff[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=1"
        ),
        "target_mb": (6, 10)
    }
}


def get_preset(name: str):
    preset = PRESETS.get(name)

    if not preset:
        raise ValueError(f"Invalid preset: {name}")

    if "filter" not in preset:
        raise ValueError(f"Preset '{name}' missing filter key")

    return preset
