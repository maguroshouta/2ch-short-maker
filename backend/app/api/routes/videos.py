import requests
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app import video_generator
from app.api.deps import get_minio
from app.models import Generate

router = APIRouter(prefix="/videos", tags=["videos"])

minio = get_minio()


@router.post("/generate")
def create_video(generate: Generate):
    try:
        id = video_generator.create_2ch_video(generate.prompt)
        minio.fput_object("videos", f"{id}.mp4", f"/tmp/{id}.mp4")
    except Exception:
        return JSONResponse(status_code=500, content={"message": "Internal server error"})
    return JSONResponse(status_code=201, content={"message": "Video created"})


@router.get("/{video_id}")
def get_video(video_id: str):
    minio_url = minio.get_presigned_url("GET", "videos", f"{video_id}.mp4")
    file_res = requests.get(minio_url)
    if file_res.status_code != 200:
        return JSONResponse(status_code=404, content={"message": "Video not found"})
    return Response(file_res.content, media_type="video/mp4")
