import os
import time
from typing import Dict

from core.config import (
    OUTPUT_DIR,
    UPLOAD_DIR,
    OUTPUT_MAX_AGE_SECONDS,
    UPLOAD_MAX_AGE_SECONDS
)


def cleanup_directory(directory: str, max_age_seconds: int) -> Dict[str, int]:
    now = time.time()
    scanned = 0
    deleted = 0
    errors = 0

    if not os.path.exists(directory):
        return {
            "scanned": scanned,
            "deleted": deleted,
            "errors": errors
        }

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)

        if not os.path.isfile(path):
            continue

        scanned += 1

        try:
            file_age = now - os.path.getmtime(path)

            if file_age > max_age_seconds:
                os.remove(path)
                deleted += 1

        except OSError:
            errors += 1

    return {
        "scanned": scanned,
        "deleted": deleted,
        "errors": errors
    }


def cleanup_uploads() -> Dict[str, int]:
    return cleanup_directory(UPLOAD_DIR, UPLOAD_MAX_AGE_SECONDS)


def cleanup_outputs() -> Dict[str, int]:
    return cleanup_directory(OUTPUT_DIR, OUTPUT_MAX_AGE_SECONDS)


def run_cleanup() -> Dict[str, Dict[str, int]]:
    return {
        "uploads": cleanup_uploads(),
        "outputs": cleanup_outputs()
    }
