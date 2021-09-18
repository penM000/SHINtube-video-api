
import shutil
from .internal.module.video.queue import add_encode_queue
from .internal.module.video.item import (
    create_directory,
    delete_directory,
    delete_video,
    update_json,
    list_video_id,
    list_link,
    get_all_info,
    get_encode_tasks,
    write_file,
    file_write_test, audio_recovery)

from .internal.module.video.encode import encoder

from fastapi import FastAPI, BackgroundTasks
from fastapi import File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

import asyncio
app = FastAPI()
#app.mount("/video", StaticFiles(directory="./video"), name="video")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

logger = logging.getLogger('api')


async def backend_file_save_add_encode(dir_path, in_file):
    # await asyncio.sleep(10)
    filename_extension = "".join(in_file.filename.split(".")[-1:])
    video_file_path = f"./{dir_path}/1.{filename_extension}"
    await write_file(video_file_path, in_file)
    await add_encode_queue(dir_path, f"1.{filename_extension}")


@app.on_event("startup")
async def startup_event():
    audio_recovery()
    tasks = await get_encode_tasks()
    for task in tasks:
        for encode_resolution in task["encode_tasks"]:
            await add_encode_queue(folderpath=task["video_directory"],
                                   filename=task["video_file_name"],
                                   encode_resolution=int(encode_resolution[:-1]))
    pass


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


@app.post("/upload")
async def post_endpoint(
        background_tasks: BackgroundTasks,
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

    created_dir = await create_directory(year, cid, title, explanation)

    background_tasks.add_task(
        backend_file_save_add_encode,
        created_dir,
        in_file)
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
    await delete_directory(year, cid, vid)
    return {"Result": "OK"}


@app.post("/updatevideo")
async def update_video(
        background_tasks: BackgroundTasks,
        year: int,
        cid: str,
        vid: str,
        title: str,
        explanation: str,
        in_file: UploadFile = File(...)):
    """
    動画修正用
    """
    await update_json(year, cid, vid, title, explanation)
    await delete_video(year, cid, vid)

    background_tasks.add_task(
        backend_file_save_add_encode,
        f"video/{year}/{cid}/{vid}",
        in_file)


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
    await update_json(year, cid, vid, title, explanation)
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


@app.get("/encodetasklist")
async def encodetasklist() -> dict:
    return await get_encode_tasks()


@app.get("/encode_test")
async def encode_test():
    return await encoder.encode_test()
