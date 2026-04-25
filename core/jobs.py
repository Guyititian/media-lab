import time
import uuid
from threading import Lock
from typing import Dict, Optional

from core.config import JOB_MAX_AGE_SECONDS

JOBS: Dict[str, dict] = {}
JOBS_LOCK = Lock()


def create_job(tool: str, preset: str, filename: str) -> str:
    job_id = str(uuid.uuid4())

    now = time.time()

    with JOBS_LOCK:
        JOBS[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "tool": tool,
            "preset": preset,
            "filename": filename,
            "output_url": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "completed_at": None,
            "duration_seconds": None
        }

    return job_id


def update_job(job_id: str, **updates) -> None:
    now = time.time()

    with JOBS_LOCK:
        if job_id not in JOBS:
            return

        job = JOBS[job_id]
        job.update(updates)
        job["updated_at"] = now

        if updates.get("status") == "processing" and not job.get("started_at"):
            job["started_at"] = now

        if updates.get("status") in {"complete", "error"}:
            job["completed_at"] = now

            started_at = job.get("started_at")
            if started_at:
                job["duration_seconds"] = round(now - started_at, 2)


def get_job(job_id: str) -> Optional[dict]:
    with JOBS_LOCK:
        job = JOBS.get(job_id)

        if not job:
            return None

        return dict(job)


def list_jobs(limit: int = 25):
    with JOBS_LOCK:
        jobs = list(JOBS.values())
        jobs.sort(key=lambda item: item.get("created_at", 0), reverse=True)
        return [dict(job) for job in jobs[:limit]]


def job_counts() -> Dict[str, int]:
    counts = {
        "total": 0,
        "queued": 0,
        "processing": 0,
        "complete": 0,
        "error": 0
    }

    with JOBS_LOCK:
        for job in JOBS.values():
            counts["total"] += 1
            status = job.get("status")

            if status in counts:
                counts[status] += 1

    return counts


def cleanup_old_jobs(max_age_seconds: int = JOB_MAX_AGE_SECONDS) -> int:
    now = time.time()

    with JOBS_LOCK:
        expired = [
            job_id
            for job_id, job in JOBS.items()
            if now - job.get("created_at", now) > max_age_seconds
        ]

        for job_id in expired:
            JOBS.pop(job_id, None)

    return len(expired)
