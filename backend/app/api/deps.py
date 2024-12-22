from minio import Minio

minio_client = Minio("localhost:9000", access_key="minio_access_key", secret_key="minio_secret_key", secure=False)


def get_minio():
    return minio_client


def init_minio():
    if minio_client.bucket_exists("videos") or minio_client.bucket_exists("thumbnails"):
        return
    minio_client.make_bucket("videos")
    minio_client.make_bucket("thumbnails")


print("Initializing Minio buckets")
init_minio()
