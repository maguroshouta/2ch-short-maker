from fastapi import APIRouter

from app.api.routes import videos

api_router = APIRouter()

api_router.include_router(videos.router)
