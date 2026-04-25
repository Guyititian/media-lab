import os

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

FFMPEG_TIMEOUT_SECONDS = int(os.getenv("FFMPEG_TIMEOUT_SECONDS", "300"))

# How long finished output files stay available.
# Default: 24 hours
OUTPUT_MAX_AGE_SECONDS = int(os.getenv("OUTPUT_MAX_AGE_SECONDS", str(60 * 60 * 24)))

# How long leftover upload files stay before cleanup.
# Default: 6 hours
UPLOAD_MAX_AGE_SECONDS = int(os.getenv("UPLOAD_MAX_AGE_SECONDS", str(60 * 60 * 6)))

# How long completed/error job records stay in memory.
# Default: 6 hours
JOB_MAX_AGE_SECONDS = int(os.getenv("JOB_MAX_AGE_SECONDS", str(60 * 60 * 6)))

ALLOWED_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".webm", ".avi",
    ".gif", ".png", ".jpg", ".jpeg", ".webp"
}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
