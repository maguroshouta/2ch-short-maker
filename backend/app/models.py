from pydantic import BaseModel


class Generate(BaseModel):
    prompt: str
