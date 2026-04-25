import os
from typing import Dict

import boto3
from botocore.exceptions import ClientError


R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_BASE_URL = os.getenv("R2_PUBLIC_BASE_URL")


def r2_configured() -> bool:
    return all([
        R2_ACCOUNT_ID,
        R2_ACCESS_KEY_ID,
        R2_SECRET_ACCESS_KEY,
        R2_BUCKET_NAME,
        R2_PUBLIC_BASE_URL
    ])


def get_r2_client():
    if not r2_configured():
        return None

    endpoint_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto"
    )


def r2_status() -> Dict:
    missing = []

    required = {
        "R2_ACCOUNT_ID": R2_ACCOUNT_ID,
        "R2_ACCESS_KEY_ID": R2_ACCESS_KEY_ID,
        "R2_SECRET_ACCESS_KEY": R2_SECRET_ACCESS_KEY,
        "R2_BUCKET_NAME": R2_BUCKET_NAME,
        "R2_PUBLIC_BASE_URL": R2_PUBLIC_BASE_URL
    }

    for key, value in required.items():
        if not value:
            missing.append(key)

    if missing:
        return {
            "enabled": False,
            "connected": False,
            "bucket": R2_BUCKET_NAME,
            "public_base_url": R2_PUBLIC_BASE_URL,
            "missing": missing,
            "message": "R2 environment variables are incomplete."
        }

    client = get_r2_client()

    try:
        client.head_bucket(Bucket=R2_BUCKET_NAME)

        return {
            "enabled": True,
            "connected": True,
            "bucket": R2_BUCKET_NAME,
            "public_base_url": R2_PUBLIC_BASE_URL,
            "missing": [],
            "message": "R2 connection successful."
        }

    except ClientError as error:
        return {
            "enabled": True,
            "connected": False,
            "bucket": R2_BUCKET_NAME,
            "public_base_url": R2_PUBLIC_BASE_URL,
            "missing": [],
            "message": str(error)
        }

    except Exception as error:
        return {
            "enabled": True,
            "connected": False,
            "bucket": R2_BUCKET_NAME,
            "public_base_url": R2_PUBLIC_BASE_URL,
            "missing": [],
            "message": str(error)
        }


def build_public_url(object_key: str) -> str:
    base = R2_PUBLIC_BASE_URL.rstrip("/")
    key = object_key.lstrip("/")
    return f"{base}/{key}"
