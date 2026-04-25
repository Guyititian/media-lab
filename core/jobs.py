import time
import uuid
from threading import Lock

JOBS = {}
JOBS_LOCK = Lock()


def create_job(tool: str, preset: str, filename: str) -> str:
    job_id = str(uuid.uuid4())

    with JOBS_LOCK:
        JOBS[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "tool": tool,
            "preset": preset,
            "filename": filename,
            "output_url": None,
            "error": None,
            "created_at": time.time(),
            "updated_at": time.time()
        }

    return job_id


def update_job(job_id: str, **updates):
    with JOBS_LOCK:
        if job_id not in JOBS:
            return

        JOBS[job_id].update(updates)
        JOBS[job_id]["updated_at"] = time.time()


def get_job(job_id: str):
    with JOBS_LOCK:
        return JOBS.get(job_id)


def cleanup_old_jobs(max_age_seconds: int = 60 * 60 * 6):
    now = time.time()

    with JOBS_LOCK:
        expired = [
            job_id
            for job_id, job in JOBS.items()
            if now - job.get("created_at", now) > max_age_seconds
        ]

        for job_id in expired:
            JOBS.pop(job_id, None)
