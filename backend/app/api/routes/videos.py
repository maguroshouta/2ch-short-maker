import uuid
from logging import getLogger

import requests
from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import JSONResponse
from sqlmodel import desc, select

from app.core import video_generator
from app.core.db import GenerateVideo, SessionDep, Video
from app.core.minio_client import get_minio

router = APIRouter(prefix="/videos", tags=["videos"])

minio = get_minio()

logger = getLogger(__name__)


@router.post("/generate")
async def create_video(session: SessionDep, request: Request, generate: GenerateVideo):
    try:
        video_path, thumbnail_path = await video_generator.create_2ch_video(generate.prompt)
        video = Video(prompt=generate.prompt)
        minio.fput_object("videos", f"{video.id}.mp4", video_path)
        minio.fput_object("thumbnails", f"{video.id}.jpg", thumbnail_path)
        session.add(video)
    except Exception as e:
        logger.exception(f"Failed to generate video: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal server error"})
    session.commit()
    session.refresh(video)
    return video


@router.get("/{video_id}.mp4")
def get_video(session: SessionDep, video_id: uuid.UUID):
    video = session.get(Video, video_id)
    if video is None:
        return JSONResponse(status_code=404, content={"message": "Video not found"})
    minio_url = minio.get_presigned_url("GET", "videos", f"{video.id}.mp4")
    file_res = requests.get(minio_url)
    if file_res.status_code != 200:
        return JSONResponse(status_code=404, content={"message": "Video not found"})
    return Response(file_res.content, media_type="video/mp4")


@router.get("/{video_id}.jpg")
def get_thumbnail(session: SessionDep, video_id: uuid.UUID):
    video = session.get(Video, video_id)
    if video is None:
        return JSONResponse(status_code=404, content={"message": "Video not found"})
    minio_url = minio.get_presigned_url("GET", "thumbnails", f"{video.id}.jpg")
    file_res = requests.get(minio_url)
    if file_res.status_code != 200:
        return JSONResponse(status_code=404, content={"message": "Thumbnail not found"})
    return Response(file_res.content, media_type="image/jpeg")


@router.get("/{video_id}")
def get_video_info(session: SessionDep, video_id: uuid.UUID):
    video = session.get(Video, video_id)
    if video is None:
        return JSONResponse(status_code=404, content={"message": "Video not found"})
    return video


@router.get("/")
def get_videos(session: SessionDep, offset=Query(default=0), limit=Query(default=20, le=20)):
    offset = int(offset)
    limit = int(limit)
    is_next = session.exec(select(Video).offset(offset + limit).limit(1)).first() is not None
    generated = session.exec(select(Video).offset(offset).limit(limit).order_by(desc(Video.created_at))).all()
    return {"is_next": is_next, "generated": generated}
