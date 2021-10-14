from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .routers import video

app = FastAPI()
app.include_router(video.router)
# app.mount("/video", StaticFiles(directory="./video"), name="video")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
