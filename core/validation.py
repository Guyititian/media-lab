import re
from pathlib import Path

from fastapi import HTTPException, UploadFile

from core.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES, MAX_UPLOAD_MB


def safe_filename(filename: str) -> str:
    name = filename or "upload"
    name = Path(name).name
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return name[:120]


def validate_upload_filename(file: UploadFile) -> str:
    filename = safe_filename(file.filename)
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}. Allowed types: {sorted(ALLOWED_EXTENSIONS)}"
        )

    return filename


def validate_upload_size(data: bytes) -> None:
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Max upload size is {MAX_UPLOAD_MB}MB."
        )
