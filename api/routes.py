import os
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks

from core.cleanup import run_cleanup
from core.config import (
    UPLOAD_DIR,
    OUTPUT_DIR,
    MAX_UPLOAD_MB,
    FFMPEG_TIMEOUT_SECONDS,
    OUTPUT_MAX_AGE_SECONDS
)
from core.jobs import (
    create_job,
    get_job,
    update_job,
    cleanup_old_jobs,
    list_jobs,
    job_counts
)
from core.presets import PRESETS
from core.redis_client import redis_status
from core.tool_schema import TOOL_DEFINITIONS
from core.validation import validate_upload_filename, validate_upload_size
from tools.gif_motion import generate_gif

router = APIRouter()


@router.get("/tools")
def get_tools():
    return {
        "success": True,
        "tools": TOOL_DEFINITIONS
    }


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found. It may have expired or the service may have restarted."
        )

    return {
        "success": True,
        "job": job
    }


@router.get("/debug/jobs")
def debug_jobs():
    return {
        "success": True,
        "counts": job_counts(),
        "jobs": list_jobs(limit=25)
    }


@router.get("/debug/redis")
def debug_redis():
    return {
        "success": True,
        "redis": redis_status()
    }


@router.get("/debug/config")
def debug_config():
    return {
        "success": True,
        "config": {
            "upload_dir": UPLOAD_DIR,
            "output_dir": OUTPUT_DIR,
            "max_upload_mb": MAX_UPLOAD_MB,
            "ffmpeg_timeout_seconds": FFMPEG_TIMEOUT_SECONDS,
            "output_max_age_seconds": OUTPUT_MAX_AGE_SECONDS,
            "available_presets": list(PRESETS.keys())
        }
    }


@router.post("/debug/cleanup")
def debug_cleanup():
    cleanup_results = run_cleanup()
    expired_jobs = cleanup_old_jobs()

    return {
        "success": True,
        "cleanup": cleanup_results,
        "expired_jobs": expired_jobs
    }


def process_gif_job(job_id: str, input_path: str, preset: str):
    try:
        update_job(job_id, status="processing")

        result = generate_gif(input_path, preset)

        update_job(
            job_id,
            status="complete",
            output_url=result["output_url"],
            error=None
        )

    except Exception as error:
        update_job(
            job_id,
            status="error",
            error=str(error)
        )

    finally:
        if input_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
            except OSError:
                pass

        run_cleanup()
        cleanup_old_jobs()


@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tool: str = Form(...),
    preset: str = Form(...)
):
    if tool != "gif_motion":
        raise HTTPException(status_code=400, detail=f"Unsupported tool: {tool}")

    if preset not in PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid preset: {preset}. Must be one of {list(PRESETS.keys())}"
        )

    clean_filename = validate_upload_filename(file)
    data = await file.read()
    validate_upload_size(data)

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{clean_filename}")

    with open(input_path, "wb") as saved_file:
        saved_file.write(data)

    job_id = create_job(
        tool=tool,
        preset=preset,
        filename=clean_filename
    )

    background_tasks.add_task(process_gif_job, job_id, input_path, preset)

    return {
        "success": True,
        "job_id": job_id,
        "status": "queued",
        "status_url": f"/jobs/{job_id}"
    }
