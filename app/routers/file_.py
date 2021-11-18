import asyncio
import re
from ..internal.video.filemanager import filemanager
from ..internal.video.database import database


from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import File, UploadFile


router = APIRouter(
    prefix="/api/file",
    tags=["file_api"],
    responses={404: {"description": "Not found"}},
)


@router.post("/fileupload")
async def fileupload_endpoint(
        cid: str,
        title: str,
        explanation: str,
        meta_data: str = "",
        year: int = None,
        service_name: str = None,
        in_file: UploadFile = File(...),):
    """
    ファイルアップロード用\n
    titleの名前がファイル名になる\n
    ディレクトリトラバース対策のため、
    引数\n
    service_name(year)    :  [年度]\n
    cid      :  [授業コード]\n
    title     : [ファイルタイトル]\n
    explanation : [ファイル説明]\n
    """
    title = re.sub(r'[\\/:*?"<>|]+', '', title)
    print(title)
    if service_name is None:
        service_name = str(year)
    created_dir = await filemanager.create_directory(
        service_name, cid, title, explanation, meta_data)
    file_path = f"./{created_dir}/{title}"
    await filemanager.write_file(file_path, in_file)
    return {"Result": "OK"}
