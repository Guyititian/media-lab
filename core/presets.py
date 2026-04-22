# core/presets.py

PRESETS = {
    # =========================================================
    # BALANCED (STABLE BASELINE - DO NOT BREAK)
    # =========================================================
    "balanced_v1": {
        "name": "balanced_v1",
        "label": "Balanced (Stable Default)",

        "fps": 24,

        "scale": "720:-2",
        "contrast": 1.05,
        "saturation": 1.10,
        "brightness": 0.00,

        # NO interpolation (keeps it fast + stable)
        "minterpolate": False,

        # palette behavior (this is your proven config)
        "palette_max_colors": 256,
        "palette_mode": "diff",

        # critical stability choice
        "dither": "bayer",
        "bayer_scale": 1,

        "yuv": "yuv420p",

        "target_mb": (4, 6)
    },

    # =========================================================
    # FLUID MOTION (RESTORED HIGH QUALITY VERSION)
    # =========================================================
    "fluid_motion_v1": {
        "name": "fluid_motion_v1",
        "label": "Fluid Motion (Stabilized Sharp)",

        # IMPORTANT: slightly safer than 50 for FFmpeg stability
        "fps": 48,

        "scale": "720:-2",

        # === QUALITY ENHANCEMENT LAYERS (RESTORED) ===
        "unsharp": True,
        "unsharp_luma_msize_x": 5,
        "unsharp_luma_msize_y": 5,
        "unsharp_luma_amount": 1.0,
        "unsharp_chroma_msize_x": 3,
        "unsharp_chroma_msize_y": 3,
        "unsharp_chroma_amount": 0.5,

        "contrast": 1.12,
        "saturation": 1.28,
        "brightness": 0.01,

        # === MOTION ENGINE (RESTORED) ===
        "minterpolate": True,
        "mi_mode": "mci",
        "mc_mode": "aobmc",
        "me_mode": "bidir",
        "vsbmc": 1,

        # === NOISE CONTROL (IMPORTANT FOR STABILITY) ===
        "hqdn3d": True,
        "hqdn3d_luma_spatial": 0.9,
        "hqdn3d_chroma_spatial": 0.9,
        "hqdn3d_luma_tmp": 2,
        "hqdn3d_chroma_tmp": 2,

        # === COLOR PIPELINE (RESTORED HIGH QUALITY) ===
        "yuv": "yuv444p",

        # === PALETTE SYSTEM (YOUR ORIGINAL GOOD RESULT) ===
        "palette_max_colors": 256,
        "palette_mode": "diff",
        "reserve_transparent": 0,

        # === DITHERING (RESTORED WORKING CHOICE) ===
        "dither": "bayer",
        "bayer_scale": 1,

        # expected output size range (prevents regression)
        "target_mb": (8, 14)
    }
}


def get_preset(name: str):
    preset = PRESETS.get(name)

    if not preset:
        raise ValueError(f"Invalid preset: {name}. Must be one of {list(PRESETS.keys())}")

    return preset
