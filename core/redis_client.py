import os
from typing import Optional

import redis


REDIS_URL = os.getenv("REDIS_URL")


def get_redis() -> Optional[redis.Redis]:
    if not REDIS_URL:
        return None

    return redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_timeout=10,
        socket_connect_timeout=10,
        retry_on_timeout=True
    )


def redis_status():
    client = get_redis()

    if not client:
        return {
            "enabled": False,
            "connected": False,
            "message": "REDIS_URL is not configured."
        }

    try:
        client.ping()
        return {
            "enabled": True,
            "connected": True,
            "message": "Redis connection successful."
        }

    except Exception as error:
        return {
            "enabled": True,
            "connected": False,
            "message": str(error)
        }
