from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
def read_root():
    return JSONResponse(content={"message": "ok"}, status_code=200)


@app.post("/generate")
def generate():
    return JSONResponse(content={"message": "ok"}, status_code=200)
