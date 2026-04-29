import mimetypes
import os
from typing import Dict, Optional

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


def r2_config_summary() -> Dict:
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

    return {
        "enabled": len(missing) == 0,
        "bucket": R2_BUCKET_NAME,
        "public_base_url": R2_PUBLIC_BASE_URL,
        "missing": missing
    }


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
    summary = r2_config_summary()

    if not summary["enabled"]:
        return {
            "enabled": False,
            "connected": False,
            "bucket": R2_BUCKET_NAME,
            "public_base_url": R2_PUBLIC_BASE_URL,
            "missing": summary["missing"],
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


def guess_content_type(local_path: str) -> str:
    content_type, _ = mimetypes.guess_type(local_path)

    if content_type:
        return content_type

    if local_path.lower().endswith(".gif"):
        return "image/gif"

    return "application/octet-stream"


def upload_file_to_r2(
    local_path: str,
    object_key: str,
    content_type: Optional[str] = None
) -> Dict:
    if not r2_configured():
        raise RuntimeError("R2 is not configured.")

    if not os.path.exists(local_path):
        raise RuntimeError(f"Local file does not exist: {local_path}")

    client = get_r2_client()

    final_content_type = content_type or guess_content_type(local_path)

    client.upload_file(
        local_path,
        R2_BUCKET_NAME,
        object_key,
        ExtraArgs={
            "ContentType": final_content_type
        }
    )

    return {
        "object_key": object_key,
        "public_url": build_public_url(object_key),
        "content_type": final_content_type
    }
