import os
import random
import string
import json
import shutil
import glob
import aiofiles
import datetime

import asyncio
from functools import wraps, partial

from fastapi import File, UploadFile

# 保存先のビデオフォルダ
video_dir = "video"


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


def remove_duplicates(_dict: dict):
    _dict["encode_tasks"] = list(set(_dict["encode_tasks"]))
    _dict["resolution"] = list(set(_dict["resolution"]))
    _dict["encode_error"] = list(set(_dict["encode_error"]))
    return _dict


def GetRandomStr(num) -> str:
    # 英数字をすべて取得
    dat = string.digits + string.ascii_lowercase + string.ascii_uppercase

    # 英数字からランダムに取得
    return ''.join([random.choice(dat) for i in range(num)])


def read_json2(json_file):
    try:
        with open(json_file) as f:
            _dict = json.load(f)
    except FileNotFoundError:
        return False
    else:
        return _dict


async def read_json(json_file):
    try:
        async with aiofiles.open(json_file, "r") as f:
            json_str = await f.read()
            _dict = json.loads(json_str)
    except FileNotFoundError:
        return False
    else:
        return _dict


def write_json(json_file, _dict):
    # 重複の削除
    _dict = remove_duplicates(_dict)
    _dict["updated_at"] = datetime.datetime.today().isoformat()
    for i in _dict["encode_tasks"]:
        if i in _dict["resolution"]:
            _dict["encode_tasks"].remove(i)

    try:
        with open(json_file, "w") as f:
            json.dump(_dict, f, indent=4)
    except BaseException:
        return False
    else:
        return True


async def write_playlist(playlist_file: str, resolution: str = "init"):
    """
    m3u8のプレイリストを作成する関数
    """
    m3u8 = {
        "init": ["#EXTM3U", "#EXT-X-VERSION:3"],
        240: [
            "#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=426x240",
            "240p.m3u8"],
        360: [
            "#EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION=640x360",
            "360p.m3u8"],
        480: [
            "#EXT-X-STREAM-INF:BANDWIDTH=4000000,RESOLUTION=854x480",
            "480p.m3u8"],
        720: [
            "#EXT-X-STREAM-INF:BANDWIDTH=7500000,RESOLUTION=1280x720",
            "720p.m3u8"],
        1080: [
            "#EXT-X-STREAM-INF:BANDWIDTH=12000000,RESOLUTION=1920x1080",
            "1080p.m3u8"],
    }
    write_data = []
    # 解像度の情報追加
    # 1080 or 1080p に対する対策
    if resolution == "init":
        write_data.extend(m3u8["init"])
        write_mode = "w"
    else:
        write_mode = "a"
        try:
            resolution = int(resolution)
        except ValueError:
            resolution = int(resolution[:-1])
        if resolution in m3u8:
            write_data.extend(m3u8[resolution])
    # 書き込み
    async with aiofiles.open(playlist_file, mode=write_mode) as f:
        # print('\n'.join(write_data))
        await f.write("\n".join(write_data) + "\n")


async def create_directory(year, cid, title, explanation) -> str:
    _created_dir = None
    while True:
        try:
            _created_dir = "/".join([video_dir, str(year),
                                     cid, GetRandomStr(10)])
            await async_wrap(os.makedirs)(_created_dir)
        except FileExistsError:
            pass
        else:
            break
    dict_template = {
        "title": title,
        "explanation": explanation,
        "created_at": datetime.datetime.today().isoformat(),
        "resolution": [],
        "encode_tasks": [],
        "encode_error": [],
    }
    write_json(_created_dir + "/info.json", dict_template)
    await write_playlist(_created_dir + "/playlist.m3u8")
    return _created_dir


async def delete_directory(year, cid, vid):
    _delete_dir = "/".join([video_dir, str(year), cid, vid])
    await async_wrap(shutil.rmtree)(_delete_dir)
    return True


async def delete_video(year, cid, vid):
    _delete_dir = "/".join([video_dir, str(year), cid, vid])
    for filepath in glob.glob(f"{_delete_dir}/*"):
        if "info.json" in filepath:
            pass
        else:
            os.remove(filepath)
    # プレイリストの初期化
    playlist_file = "/".join([video_dir, str(year), cid, vid, "playlist.m3u8"])
    await write_playlist(playlist_file)
    # 既存のjsonを読み込み
    json_file = "/".join([video_dir, str(year), cid, vid, "info.json"])
    _dict = await read_json(json_file)
    if not _dict:
        return False
    # jsonの更新
    _dict["resolution"] = []
    _dict["encode_tasks"] = []
    _dict["encode_error"] = []

    # jsonの書き込み
    if write_json(json_file, _dict):
        return True
    return False


async def update_json(year, cid, vid, title, explanation):
    # 既存のjsonを読み込み
    json_file = "/".join([video_dir, str(year), cid, vid, "info.json"])
    _dict = await read_json(json_file)
    if not _dict:
        return False
    # jsonの更新
    _dict["title"] = title
    _dict["explanation"] = explanation
    # jsonの書き込み
    if write_json(json_file, _dict):
        return True
    return False


async def list_video_id(year, cid):
    _video_dir = "/".join([video_dir, str(year), cid])
    temp = await async_wrap(glob.glob)(f"{_video_dir}/*")
    return [video_id.split("/")[-1]
            for video_id in temp]


async def list_link(year, cid):
    _video_dir = "/".join([video_dir, str(year), cid])
    temp = await async_wrap(glob.glob)(f"{_video_dir}/*")
    result = {}
    for link_path in temp:
        json_file = link_path + "/info.json"
        try:
            async with aiofiles.open(json_file, "r") as f:
                json_str = await f.read()
                _dict = json.loads(json_str)
        except FileNotFoundError:
            pass
        else:
            result[link_path.split("/")[-1]] = _dict
    return result


async def result_encode(folderpath, resolution, result=True):
    # 既存のjsonを読み込み
    json_file = "/".join([folderpath, "info.json"])
    _dict = await read_json(json_file)

    if not _dict:
        return False
    if result:
        # 画質の追加
        _dict["resolution"].append(f"{resolution}p")
        _dict["encode_tasks"].remove(f"{resolution}p")
    else:
        _dict["encode_error"].append(f"{resolution}p")
        _dict["encode_tasks"].remove(f"{resolution}p")
    # jsonの書き込み
    write_json(json_file, _dict)
    # プレイリストに書き込み
    playlist = "/".join([folderpath, "playlist.m3u8"])
    await write_playlist(playlist, resolution)


async def add_encode_task(folderpath, resolution):
    # 既存のjsonを読み込み
    json_file = "/".join([folderpath, "info.json"])
    _dict = await read_json(json_file)
    if not _dict:
        return False
    if f"{resolution}p" in _dict["resolution"]:
        return True
    # 画質の追加
    _dict["encode_tasks"].append(f"{resolution}p")
    # jsonの書き込み
    if write_json(json_file, _dict):
        return True
    return False


async def get_all_info():
    json_files_path = await async_wrap(glob.glob)(
        f"./{video_dir}/**/info.json",
        recursive=True)
    result = []
    for json_file in json_files_path:
        temp = await read_json(json_file)

        directory = "/".join(json_file.split("/")[:-1])
        temp["video_directory"] = directory
        try:
            temp["video_file_name"] = glob.glob(
                f"{directory}/1.*")[0].split("/")[-1]
        except IndexError:
            temp["video_file_name"] = None
        result.append(temp)
    return result


async def get_encode_tasks():
    video_info = await get_all_info()
    result = []
    for info in video_info:
        if len(info["encode_tasks"]) > 0:
            result.append(info)
    return result


async def write_file(file_path, in_file: UploadFile = File(...)):
    async with aiofiles.open(file_path, 'wb') as out_file:
        while True:
            # 書き込みサイズ(MB)
            chunk = 32
            content = await in_file.read(chunk * 1048576)  # async read chunk
            if content:
                await out_file.write(content)  # async write chunk
            else:
                break
