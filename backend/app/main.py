from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.db import create_db_and_tables
from app.core.env import FRONTEND_URL
from app.core.minio_client import create_bucket


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    create_bucket()
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
