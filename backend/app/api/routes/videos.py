from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app import video_generator
from app.models import Generate

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/generate")
def create_video(generate: Generate):
    try:
        video_generator.create_2ch_video(generate.prompt)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "Internal server error"})
    return JSONResponse(status_code=201, content={"message": "Video created"})
