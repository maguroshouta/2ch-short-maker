from minio import Minio

from app.core.env import MINIO_ACCESS_KEY, MINIO_API_URL, MINIO_SECRET_KEY

minio_client = Minio(MINIO_API_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)


def get_minio():
    return minio_client


def create_bucket():
    if not minio_client.bucket_exists("videos"):
        minio_client.make_bucket("videos")
    if not minio_client.bucket_exists("thumbnails"):
        minio_client.make_bucket("thumbnails")
