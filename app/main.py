
from .internal.module.video.queue import add_encode_queue
from .internal.module.video.item import (
    create_directory,
    delete_directory,
    delete_video,
    update_json,
    list_video_id, list_link)

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


@app.on_event("startup")
async def startup_event():
    pass


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


@app.post("/upload")
async def post_endpoint(
        year: int,
        cid: str,
        title: str,
        explanation: str,
        in_file: UploadFile = File(...),):
    """
    動画アップロード用\n
    \n
    引数\n
    in_file :  [動画ファイル]\n
    year    :  [年度]\n
    cid      :  [授業コード]\n
    title     : [動画タイトル]\n
    explanation : [動画説明]\n
    """

    created_dir = create_directory(year, cid, title, explanation)
    filename_extension = "".join(in_file.filename.split(".")[-1:])
    video_file_path = f"./{created_dir}/1.{filename_extension}"
    async with aiofiles.open(video_file_path, 'wb') as out_file:
        while True:
            # 書き込みサイズ(MB)
            chunk = 4
            content = await in_file.read(chunk * 1048576)  # async read chunk
            if content:
                await out_file.write(content)  # async write chunk
            else:
                break

    # await add_encode_queue("./video", "1.mp4", height=360)
    await add_encode_queue(f"./{created_dir}", f"1.{filename_extension}", height=160)

    return {"Result": "OK"}


@app.post("/delete")
async def video_delete(year: int, cid: str, vid: str):
    """
    動画削除用\n

    引数\n
    year    :  [年度]\n
    cid      :  [授業コード]\n
    vid      :  [動画コード]\n
    """
    delete_directory(year, cid, vid)
    return {"Result": "OK"}


@app.post("/updatevideo")
async def update_video(
        year: int,
        cid: str,
        vid: str,
        in_file: UploadFile = File(...)):
    """
    動画修正用
    """
    delete_video(year, cid, vid)
    filename_extension = "".join(in_file.filename.split(".")[-1:])

    async with aiofiles.open(f"video/{year}/{cid}/{vid}/1.{filename_extension}", 'wb') as out_file:
        while True:
            # 書き込みサイズ(MB)
            chunk = 4
            content = await in_file.read(chunk * 1048576)  # async read chunk
            if content:
                await out_file.write(content)  # async write chunk
            else:
                break

    # await add_encode_queue("./video", "1.mp4", height=360)
    await add_encode_queue(f"video/{year}/{cid}/{vid}", f"1.{filename_extension}", height=160)


@app.post("/updateinfo")
async def update_info(
        year: int,
        cid: str,
        vid: str,
        title: str,
        explanation: str,
):
    """
    info修正用
    """
    update_json(year, cid, vid, title, explanation)
    return {"Result": "OK"}


@app.get("/videolist")
async def video_list(year: int, cid: str):
    """
    動画一覧取得用
    """

    return await list_video_id(year, cid)


@app.get("/linklist")
async def linklist(year: int, cid: str):
    return await list_link(year, cid)
