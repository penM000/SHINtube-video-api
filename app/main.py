
from .internal.module.video.filemanager import filemanager
from .internal.module.video.database import database
from .internal.module.video.queue import add_encode_queue
from .internal.module.video.recovery import recovery
from .internal.module.video.encode import encoder

from fastapi import FastAPI, BackgroundTasks
from fastapi import File, UploadFile
from starlette.middleware.cors import CORSMiddleware


app = FastAPI()
# app.mount("/video", StaticFiles(directory="./video"), name="video")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)


async def backend_file_save_add_encode(dir_path, in_file):
    filename_extension = "".join(in_file.filename.split(".")[-1:])
    video_file_path = f"./{dir_path}/1.{filename_extension}"
    await filemanager.write_file(video_file_path, in_file)
    await add_encode_queue(dir_path, f"1.{filename_extension}")


@app.on_event("startup")
async def startup_event():
    await recovery.runrecovery()


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
    created_dir = await filemanager.create_directory(
        year, cid, title, explanation)

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
    await filemanager.delete_directory(year, cid, vid)
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
    await database.update_info(year, cid, vid, title, explanation)
    await database.delete_video(year, cid, vid)

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
    await database.update_info(year, cid, vid, title, explanation)
    return {"Result": "OK"}


@app.get("/videolist")
async def video_list(year: int, cid: str):
    """
    動画一覧取得用
    """

    return await database.list_video_id(year, cid)


@app.get("/linklist")
async def linklist(year: int, cid: str):
    return await database.list_link(year, cid)


@app.get("/encodetasklist")
async def encodetasklist() -> dict:
    return await database.get_encode_tasks()


@app.get("/encode_test")
async def encode_test():
    return await encoder.encode_test()
