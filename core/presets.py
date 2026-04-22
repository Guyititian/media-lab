# core/presets.py

PRESETS = {
    "balanced_v1": {
        "name": "balanced_v1",
        "fps": 24,

        "scale": "720:-2",
        "contrast": 1.05,
        "saturation": 1.10,
        "brightness": 0.00,

        "minterpolate": False,

        "palette_max_colors": 256,
        "palette_mode": "diff",

        "dither": "bayer",
        "bayer_scale": 1,

        "yuv": "yuv420p",

        "target_mb": (4, 6)
    },

    "fluid_motion_v1": {
        "name": "fluid_motion_v1",
        "fps": 50,

        # higher fidelity motion interpolation
        "scale": "720:-2",
        "contrast": 1.08,
        "saturation": 1.22,
        "brightness": 0.01,

        "minterpolate": True,
        "mi_mode": "mci",
        "mc_mode": "aobmc",
        "me_mode": "bidir",
        "vsbmc": 1,

        # IMPORTANT FIX:
        # prevents under-coloring (your 600KB regression)
        "palette_max_colors": 256,
        "palette_mode": "diff",

        # FIX: remove aggressive dithering collapse
        "dither": "floyd_steinberg",

        "yuv": "yuv444p",

        # prevents over-compression
        "target_mb": (8, 14)
    }
}


def get_preset(name: str):
    preset = PRESETS.get(name)

    if not preset:
        raise ValueError(f"Invalid preset: {name}. Must be one of {list(PRESETS.keys())}")

    return preset
