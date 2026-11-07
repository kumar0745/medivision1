from pathlib import Path
from uuid import uuid4
import boto3
from botocore.config import Config
from .config import settings

def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.aws_endpoint_url_s3,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )

def store_file(user_id: int, extension: str, content: bytes, content_type: str) -> str:
    key = f"users/{user_id}/{uuid4().hex}{extension}"
    if settings.storage_backend.lower() == "s3":
        _s3_client().put_object(
            Bucket=settings.s3_bucket, Key=key, Body=content,
            ContentType=content_type, ContentDisposition="attachment",
            Metadata={"owner-id": str(user_id)},
        )
        return key
    root = Path(settings.upload_dir).resolve()
    target = (root / key).resolve()
    if root not in target.parents:
        raise ValueError("Invalid storage key.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return key

def delete_file(key: str) -> None:
    if settings.storage_backend.lower() == "s3":
        _s3_client().delete_object(Bucket=settings.s3_bucket, Key=key)
        return
    root = Path(settings.upload_dir).resolve()
    target = (root / key).resolve()
    if root in target.parents and target.is_file():
        target.unlink()

def signed_download_url(key: str) -> str:
    return _s3_client().generate_presigned_url(
        "get_object", Params={"Bucket": settings.s3_bucket, "Key": key}, ExpiresIn=60,
    )

def local_file_path(key: str) -> Path:
    root = Path(settings.upload_dir).resolve()
    target = (root / key).resolve()
    if root not in target.parents:
        raise ValueError("Invalid storage key.")
    return target
