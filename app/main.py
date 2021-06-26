from .internal.module.video.encode import encode
from .internal.module.video.queue import add_encode_queue
import aiofiles
from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/video", StaticFiles(directory="./video"), name="video")
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


@app.post("/upload")
async def post_endpoint(in_file: UploadFile = File(...)):

    async with aiofiles.open("./video/1.mp4", 'wb') as out_file:
        while True:
            # 書き込みサイズ(MB)
            chunk = 4
            content = await in_file.read(chunk * 1048576)  # async read chunk
            if content:
                await out_file.write(content)  # async write chunk
            else:
                break
    
    #await add_encode_queue("./video", "1.mp4", height=360)
    await add_encode_queue("./video", "1.mp4", height=160)

    return {"Result": "OK"}
