from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine

from app.core.env import DATABASE_URL


class GenerateVideo(SQLModel):
    prompt: str


class Video(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    prompt: str
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)


ECHO_LOG = True

engine = create_engine(DATABASE_URL, echo=ECHO_LOG)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
