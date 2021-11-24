import asyncio
import pathlib

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import File, UploadFile

from ..internal.module.general_module import general_module
from ..internal.video.filemanager import filemanager
from ..internal.video.database import database
from ..internal.video.queue import queue
from ..internal.video.recovery import recovery
from ..internal.video.encode import encoder

router = APIRouter(
    prefix="/api/video",
    tags=["video_api"],
    responses={404: {"description": "Not found"}},
)


async def backend_file_save_add_encode(dir_path, in_file):
    filename_extension = "".join(in_file.filename.split(".")[-1:])
    video_file_path = f"./{dir_path}/original_video.{filename_extension}"
    await filemanager.write_file(video_file_path, in_file)
    await queue.add_original_video(dir_path,
                                   f"original_video.{filename_extension}")


@router.on_event("startup")
async def startup_event():
    await encoder.encode_test()
    await recovery.runrecovery()
    task = filemanager.delete_original_video_task(60)
    asyncio.create_task(task)


@router.post("/upload")
async def upload_endpoint(
        background_tasks: BackgroundTasks,
        cid: str,
        title: str,
        explanation: str,
        meta_data: str = "",
        year: int = None,
        service_name: str = None,
        in_file: UploadFile = File(...),):
    """
    動画アップロード用\n
    \n
    引数\n
    in_file :  [動画ファイル]\n
    service_name(year)    :  [年度]\n
    cid      :  [授業コード]\n
    title     : [動画タイトル]\n
    explanation : [動画説明]\n
    """
    if service_name is None:
        service_name = str(year)
    created_dir = await filemanager.create_directory(
        service_name, cid, title, explanation, meta_data)

    background_tasks.add_task(
        backend_file_save_add_encode,
        created_dir,
        in_file)
    created_dir_path = pathlib.Path(created_dir)
    vid = created_dir_path.name
    return {"Result": "OK", "vid": vid}


@router.post("/emptyfileupload")
async def emptyupload_endpoint(
        cid: str,
        title: str,
        explanation: str,
        meta_data: str = "",
        year: int = None,
        service_name: str = None,):
    """
    空のinfo.json作成用\n
    あとから、updatevideo・updateinfoが可能\n
    引数\n
    service_name(year)    :  [年度]\n
    cid      :  [授業コード]\n
    title     : [動画タイトル]\n
    explanation : [動画説明]\n
    """
    if service_name is None:
        service_name = str(year)
    created_dir = await filemanager.create_directory(
        service_name, cid, title, explanation, meta_data)
    created_dir_path = pathlib.Path(created_dir)
    (created_dir_path / "emptyfile").touch()
    vid = created_dir_path.name
    return {"Result": "OK", "vid": vid}


@router.post("/delete")
async def video_delete(cid: str,
                       vid: str,
                       year: int = None,
                       service_name: str = None):
    """
    動画削除用\n

    引数\n
    service_name(year)    :  [年度]\n
    cid      :  [授業コード]\n
    vid      :  [動画コード]\n
    """
    if service_name is None:
        service_name = str(year)
    await filemanager.delete_directory(service_name, cid, vid)
    return {"Result": "OK"}


@router.post("/updatevideo")
async def update_video(
        background_tasks: BackgroundTasks,
        cid: str,
        vid: str,
        title: str,
        explanation: str,
        meta_data: str = "",
        year: int = None,
        service_name: str = None,
        in_file: UploadFile = File(...)):
    """
    動画修正用
    """
    if service_name is None:
        service_name = str(year)
    # meta_dataが空であれば更新しない
    if meta_data == "":
        json_file = "/".join([filemanager.video_dir, str(service_name),
                              cid, vid, "info.json"])
        json_data = await general_module.read_json(json_file)
        meta_data = json_data["meta_data"]
    await database.update_info(service_name,
                               cid, vid, title,
                               explanation, meta_data)
    await database.delete_video(service_name, cid, vid)

    background_tasks.add_task(
        backend_file_save_add_encode,
        f"video/{service_name}/{cid}/{vid}",
        in_file)


@router.post("/updateinfo")
async def update_info(
        cid: str,
        vid: str,
        title: str,
        explanation: str,
        year: int = None,
        service_name: str = None,
        meta_data: str = "",
):
    """
    info修正用
    """
    if service_name is None:
        service_name = str(year)
    # meta_dataが空であれば更新しない
    if meta_data == "":
        json_file = "/".join([filemanager.video_dir, service_name,
                              cid, vid, "info.json"])
        json_data = await general_module.read_json(json_file)
        meta_data = json_data["meta_data"]
    await database.update_info(
        service_name,
        cid,
        vid,
        title,
        explanation,
        meta_data)
    return {"Result": "OK"}


@router.get("/videolist")
async def video_list(
        cid: str,
        year: int = None,
        service_name: str = None,):
    """
    動画一覧取得用
    """
    if service_name is None:
        service_name = str(year)
    return await database.list_video_id(service_name, cid)


@router.get("/linklist")
async def linklist(
        cid: str,
        year: int = None,
        service_name: str = None,):
    if service_name is None:
        service_name = str(year)
    return await database.list_link(service_name, cid)


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


@router.get("/getall")
async def getall() -> dict:
    return await database.get_all_info()
