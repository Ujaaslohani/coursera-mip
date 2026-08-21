"""Object storage abstraction, per doc §6.2 (Pixeltable/Postgres/Supabase/
object storage) and §5.4 'Object storage' data asset. Every asset's media
lives behind this interface rather than a bare repo-relative path, so the
backend never assumes local disk access — swapping in real cloud storage is
a one-class change, not a rewrite.

Backend selection: `get_storage_backend()` returns an S3-compatible backend
whenever OBJECT_STORAGE_URL/OBJECT_STORAGE_KEY are configured, and falls
back to a local-filesystem backend otherwise (both `.env.example` and this
environment's `.env` ship those two vars empty — no cloud object-storage
credentials exist here, so LocalFilesystemStorage is what's actually live).
"""
import os
import shutil
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


class StorageBackend(ABC):
    @abstractmethod
    def put(self, local_path: str, key: str | None = None) -> str:
        """Store a file, returning its storage_url reference."""

    @abstractmethod
    def resolve(self, storage_url: str) -> Path:
        """Resolve a storage_url back to a local path for processing."""

    @abstractmethod
    def exists(self, storage_url: str) -> bool:
        ...


class LocalFilesystemStorage(StorageBackend):
    """Stand-in object store: files live under data/object_store/, addressed
    by a storage_url of the form local://<key>. This is the backend actually
    in effect in this environment (see module docstring)."""

    def __init__(self, root: Path | None = None):
        self.root = root or (REPO_ROOT / "data" / "object_store")
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, local_path: str, key: str | None = None) -> str:
        src = Path(local_path)
        key = key or f"{uuid.uuid4()}{src.suffix}"
        dest = self.root / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return f"local://{key}"

    def resolve(self, storage_url: str) -> Path:
        if storage_url.startswith("local://"):
            return self.root / storage_url.removeprefix("local://")
        # Back-compat: pre-existing sample assets use bare repo-relative paths
        # registered before this storage layer existed.
        return REPO_ROOT / storage_url

    def exists(self, storage_url: str) -> bool:
        return self.resolve(storage_url).exists()


class S3CompatibleStorage(StorageBackend):
    """Real object storage (S3-compatible — e.g. Supabase Storage, MinIO, AWS
    S3 itself). Requires OBJECT_STORAGE_URL (endpoint) and OBJECT_STORAGE_KEY
    (used as both access key and secret, matching this project's single-var
    `.env` convention). Not exercised in this environment — no credentials
    are configured — but implements the same interface as
    LocalFilesystemStorage so it's a drop-in replacement once they are.
    """

    def __init__(self, endpoint_url: str, key: str, bucket: str = "mip-assets"):
        import boto3  # imported lazily — boto3 is only needed if this backend is actually selected

        self.client = boto3.client(
            "s3", endpoint_url=endpoint_url, aws_access_key_id=key, aws_secret_access_key=key
        )
        self.bucket = bucket

    def put(self, local_path: str, key: str | None = None) -> str:
        key = key or f"{uuid.uuid4()}{Path(local_path).suffix}"
        self.client.upload_file(local_path, self.bucket, key)
        return f"s3://{self.bucket}/{key}"

    def resolve(self, storage_url: str) -> Path:
        import tempfile

        bucket, _, key = storage_url.removeprefix("s3://").partition("/")
        tmp = Path(tempfile.gettempdir()) / f"mip-download-{uuid.uuid4()}{Path(key).suffix}"
        self.client.download_file(bucket, key, str(tmp))
        return tmp

    def exists(self, storage_url: str) -> bool:
        bucket, _, key = storage_url.removeprefix("s3://").partition("/")
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except Exception:
            return False


def get_storage_backend() -> StorageBackend:
    endpoint = os.environ.get("OBJECT_STORAGE_URL")
    key = os.environ.get("OBJECT_STORAGE_KEY")
    if endpoint and key:
        return S3CompatibleStorage(endpoint, key)
    return LocalFilesystemStorage()
