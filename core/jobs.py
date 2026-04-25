import json
import time
import uuid
from threading import Lock
from typing import Dict, Optional

from core.config import JOB_MAX_AGE_SECONDS
from core.redis_client import get_redis


JOBS: Dict[str, dict] = {}
JOBS_LOCK = Lock()

JOB_KEY_PREFIX = "media_lab:job:"
RECENT_JOBS_KEY = "media_lab:jobs:recent"


def _now() -> float:
    return time.time()


def _job_key(job_id: str) -> str:
    return f"{JOB_KEY_PREFIX}{job_id}"


def _redis():
    return get_redis()


def _save_job_redis(job: dict) -> None:
    client = _redis()
    if not client:
        return

    job_id = job["job_id"]
    client.set(
        _job_key(job_id),
        json.dumps(job),
        ex=JOB_MAX_AGE_SECONDS
    )
    client.zadd(RECENT_JOBS_KEY, {job_id: job.get("created_at", _now())})


def _get_job_redis(job_id: str) -> Optional[dict]:
    client = _redis()
    if not client:
        return None

    raw = client.get(_job_key(job_id))
    if not raw:
        return None

    return json.loads(raw)


def create_job(tool: str, preset: str, filename: str) -> str:
    job_id = str(uuid.uuid4())
    now = _now()

    job = {
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

    client = _redis()

    if client:
        _save_job_redis(job)
    else:
        with JOBS_LOCK:
            JOBS[job_id] = job

    return job_id


def update_job(job_id: str, **updates) -> None:
    now = _now()
    client = _redis()

    if client:
        job = _get_job_redis(job_id)

        if not job:
            return

        job.update(updates)
        job["updated_at"] = now

        if updates.get("status") == "processing" and not job.get("started_at"):
            job["started_at"] = now

        if updates.get("status") in {"complete", "error"}:
            job["completed_at"] = now

            started_at = job.get("started_at")
            if started_at:
                job["duration_seconds"] = round(now - started_at, 2)

        _save_job_redis(job)
        return

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
    client = _redis()

    if client:
        return _get_job_redis(job_id)

    with JOBS_LOCK:
        job = JOBS.get(job_id)

        if not job:
            return None

        return dict(job)


def list_jobs(limit: int = 25):
    client = _redis()

    if client:
        job_ids = client.zrevrange(RECENT_JOBS_KEY, 0, limit - 1)
        jobs = []

        for job_id in job_ids:
            job = _get_job_redis(job_id)
            if job:
                jobs.append(job)

        return jobs

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

    jobs = list_jobs(limit=100)

    for job in jobs:
        counts["total"] += 1
        status = job.get("status")

        if status in counts:
            counts[status] += 1

    return counts


def cleanup_old_jobs(max_age_seconds: int = JOB_MAX_AGE_SECONDS) -> int:
    now = _now()
    cutoff = now - max_age_seconds
    client = _redis()

    if client:
        expired_job_ids = client.zrangebyscore(RECENT_JOBS_KEY, 0, cutoff)

        for job_id in expired_job_ids:
            client.delete(_job_key(job_id))

        if expired_job_ids:
            client.zrem(RECENT_JOBS_KEY, *expired_job_ids)

        return len(expired_job_ids)

    with JOBS_LOCK:
        expired = [
            job_id
            for job_id, job in JOBS.items()
            if now - job.get("created_at", now) > max_age_seconds
        ]

        for job_id in expired:
            JOBS.pop(job_id, None)

    return len(expired)
