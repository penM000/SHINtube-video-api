from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .routers import video
from .routers import videolegacy
from .routers import file_

description = """
SHINtube-video-api は、様々な形式の動画をHLSで再生できるように変換・配信するシステムです。


## video_api

You can **read items**.

## file_api
限定的なfileapiです。
videoapiと同居しており、削除などはvideoapiと兼用です。
"""
tags_metadata = [{"name": "video_api",
                  "description": "動画アップロード・管理用",
                  },
                 {"name": "file_api",
                  "description": "限定的なファイルアップロード機能",
                  },
                 ]
app = FastAPI(title="SHINtube-video-api",
              description=description,
              version="0.0.1",
              terms_of_service="https://github.com/penM000/SHINtube-video-api",
              license_info={
                  "name": "MIT License",
                  "url": "https://opensource.org/licenses/mit-license.php",
              },
              openapi_tags=tags_metadata)
app.include_router(video.router)
# app.include_router(videolegacy.router)
# app.include_router(file_.router)
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
