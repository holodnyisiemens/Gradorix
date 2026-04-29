from app.minio.minio_client import minio_client
from app.core.config import settings

def init_bucket():
    if not minio_client.bucket_exists(settings.MINIO_BUCKET):
        minio_client.make_bucket(settings.MINIO_BUCKET)

