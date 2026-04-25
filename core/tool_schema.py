from core.presets import PRESETS

TOOL_DEFINITIONS = {
    "gif_motion": {
        "name": "GIF Motion Engine",
        "description": "Convert user media into optimized animated GIFs with selectable presets.",
        "presets": {
            key: {
                "label": value["label"],
                "description": value["description"]
            }
            for key, value in PRESETS.items()
        }
    }
}
