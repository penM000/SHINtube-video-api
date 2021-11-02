
from ..internal.module.video.filemanager import filemanager
from ..internal.module.video.database import database
from ..internal.module.video.queue import add_encode_queue
from ..internal.module.video.recovery import recovery
from ..internal.module.video.encode import encoder


from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import File, UploadFile
import asyncio
router = APIRouter(
    prefix="",
    tags=["video_api"],
    responses={404: {"description": "Not found"}},
)


async def backend_file_save_add_encode(dir_path, in_file):
    filename_extension = "".join(in_file.filename.split(".")[-1:])
    video_file_path = f"./{dir_path}/1.{filename_extension}"
    await filemanager.write_file(video_file_path, in_file)
    await add_encode_queue(dir_path, f"1.{filename_extension}")


@router.on_event("startup")
async def startup_event():
    await recovery.runrecovery()
    task = filemanager.delete_original_video_task(60)
    asyncio.create_task(task)


@router.post("/upload")
async def post_endpoint(
        background_tasks: BackgroundTasks,
        year: int,
        cid: str,
        title: str,
        explanation: str,
        meta_data: str = "",
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
        year, cid, title, explanation, meta_data)

    background_tasks.add_task(
        backend_file_save_add_encode,
        created_dir,
        in_file)
    return {"Result": "OK"}


@router.post("/delete")
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


@router.post("/updatevideo")
async def update_video(
        background_tasks: BackgroundTasks,
        year: int,
        cid: str,
        vid: str,
        title: str,
        explanation: str,
        meta_data: str = "",
        in_file: UploadFile = File(...)):
    """
    動画修正用
    """
    # meta_dataが空であれば更新しない
    if meta_data == "":
        json_file = "/".join([filemanager.video_dir, str(year),
                              cid, vid, "info.json"])
        json_data = await filemanager.read_json(json_file)
        meta_data = json_data["meta_data"]
    await database.update_info(year, cid, vid, title, explanation, meta_data)
    await database.delete_video(year, cid, vid)

    background_tasks.add_task(
        backend_file_save_add_encode,
        f"video/{year}/{cid}/{vid}",
        in_file)


@router.post("/updateinfo")
async def update_info(
        year: int,
        cid: str,
        vid: str,
        title: str,
        explanation: str,
        meta_data: str = "",
):
    """
    info修正用
    """
    # meta_dataが空であれば更新しない
    if meta_data == "":
        json_file = "/".join([filemanager.video_dir, str(year),
                              cid, vid, "info.json"])
        json_data = await filemanager.read_json(json_file)
        meta_data = json_data["meta_data"]
    await database.update_info(year, cid, vid, title, explanation, meta_data)
    return {"Result": "OK"}


@router.get("/videolist")
async def video_list(year: int, cid: str):
    """
    動画一覧取得用
    """

    return await database.list_video_id(year, cid)


@router.get("/linklist")
async def linklist(year: int, cid: str):
    return await database.list_link(year, cid)


@router.get("/encodetasklist")
async def encodetasklist() -> dict:
    return await database.get_encode_tasks()


@router.get("/encode_test")
async def encode_test():
    return await encoder.encode_test()


@router.get("/encoder_status")
async def encoder_status():
    return {"encoder_used_status": encoder.encoder_used_status,
            "encoder_available": encoder.encoder_available}
