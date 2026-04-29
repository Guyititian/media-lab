import mimetypes
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
from core.r2_storage import (
    r2_status,
    upload_file_to_r2,
    upload_bytes_to_r2,
    download_file_from_r2,
    delete_object_from_r2,
    r2_config_summary
)
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


@router.get("/debug/r2")
def debug_r2():
    return {
        "success": True,
        "r2": r2_status()
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
            "available_presets": list(PRESETS.keys()),
            "r2": r2_config_summary()
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


def get_content_type(filename: str) -> str:
    content_type, _ = mimetypes.guess_type(filename)

    if content_type:
        return content_type

    return "application/octet-stream"


def process_gif_job(
    job_id: str,
    preset: str,
    input_object_key: str = None,
    local_input_path: str = None
):
    working_input_path = local_input_path
    local_output_path = None

    try:
        update_job(job_id, status="processing")

        if input_object_key:
            download_name = f"{job_id}_{os.path.basename(input_object_key)}"
            working_input_path = os.path.join(UPLOAD_DIR, download_name)

            download_file_from_r2(
                object_key=input_object_key,
                local_path=working_input_path
            )

            update_job(
                job_id,
                input_downloaded=True
            )

        if not working_input_path or not os.path.exists(working_input_path):
            raise RuntimeError("Input file was not available for processing.")

        result = generate_gif(working_input_path, preset)

        local_output_path = result["output_path"]
        local_output_url = result["output_url"]

        output_filename = os.path.basename(local_output_path)
        r2_object_key = f"outputs/{output_filename}"

        try:
            r2_result = upload_file_to_r2(
                local_path=local_output_path,
                object_key=r2_object_key,
                content_type="image/gif"
            )

            update_job(
                job_id,
                status="complete",
                output_url=r2_result["public_url"],
                output_storage="r2",
                output_key=r2_result["object_key"],
                error=None
            )

            try:
                os.remove(local_output_path)
            except OSError:
                pass

        except Exception as r2_error:
            update_job(
                job_id,
                status="complete",
                output_url=local_output_url,
                output_storage="local_fallback",
                output_key=None,
                storage_warning=f"R2 output upload failed, using local fallback: {str(r2_error)}",
                error=None
            )

    except Exception as error:
        update_job(
            job_id,
            status="error",
            error=str(error)
        )

    finally:
        if working_input_path and os.path.exists(working_input_path):
            try:
                os.remove(working_input_path)
            except OSError:
                pass

        if input_object_key:
            try:
                delete_object_from_r2(input_object_key)
                update_job(
                    job_id,
                    input_deleted=True
                )
            except Exception as delete_error:
                update_job(
                    job_id,
                    input_delete_warning=str(delete_error)
                )

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

    job_id = create_job(
        tool=tool,
        preset=preset,
        filename=clean_filename
    )

    input_object_key = None
    local_input_path = None

    try:
        input_object_key = f"inputs/{job_id}/{clean_filename}"

        upload_bytes_to_r2(
            data=data,
            object_key=input_object_key,
            content_type=get_content_type(clean_filename)
        )

        update_job(
            job_id,
            input_storage="r2",
            input_key=input_object_key
        )

    except Exception as r2_error:
        file_id = str(uuid.uuid4())
        local_input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{clean_filename}")

        with open(local_input_path, "wb") as saved_file:
            saved_file.write(data)

        update_job(
            job_id,
            input_storage="local_fallback",
            input_key=None,
            storage_warning=f"R2 input upload failed, using local fallback: {str(r2_error)}"
        )

    background_tasks.add_task(
        process_gif_job,
        job_id,
        preset,
        input_object_key,
        local_input_path
    )

    return {
        "success": True,
        "job_id": job_id,
        "status": "queued",
        "status_url": f"/jobs/{job_id}"
    }
