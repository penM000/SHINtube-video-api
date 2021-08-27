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


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


# 保存先のビデオフォルダ
video_dir = "video"


def GetRandomStr(num) -> str:
    # 英数字をすべて取得
    dat = string.digits + string.ascii_lowercase + string.ascii_uppercase

    # 英数字からランダムに取得
    return ''.join([random.choice(dat) for i in range(num)])


def read_json(json_file):
    try:
        with open(json_file) as f:
            _dict = json.load(f)
    except FileNotFoundError:
        return False
    else:
        return _dict


def write_json(json_file, _dict):
    try:
        with open(json_file, "w") as f:
            json.dump(_dict, f, indent=4)
    except BaseException:
        return False
    else:
        return True


def write_playlist(playlist_file: str, _list: list, add=False):
    if add:
        mode = "a"
    else:
        mode = "w"
    with open(playlist_file, mode) as f:
        f.writelines('\n'.join(_list))
        f.write("\n")


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
        "updated_at": datetime.datetime.today().isoformat(),
        "resolution": [],
        "encode_tasks": [],
        "encode_error": [],
    }
    write_json(_created_dir + "/info.json", dict_template)
    playlist_template = ["#EXTM3U", "#EXT-X-VERSION:3"]
    write_playlist(_created_dir + "/playlist.m3u8", playlist_template)
    return _created_dir


async def delete_directory(year, cid, vid):
    _delete_dir = "/".join([video_dir, str(year), cid, vid])
    await async_wrap(shutil.rmtree)(_delete_dir)
    return True


def delete_video(year, cid, vid):
    _delete_dir = "/".join([video_dir, str(year), cid, vid])
    for filepath in glob.glob(f"{_delete_dir}/*"):
        if "info.json" in filepath:
            pass
        else:
            os.remove(filepath)
    # プレイリストの初期化
    playlist_file = "/".join([video_dir, str(year), cid, vid, "playlist.m3u8"])
    playlist_template = ["#EXTM3U", "#EXT-X-VERSION:3"]
    write_playlist(playlist_file, playlist_template)
    # 既存のjsonを読み込み
    json_file = "/".join([video_dir, str(year), cid, vid, "info.json"])
    _dict = read_json(json_file)
    if not _dict:
        return False
    # jsonの更新
    _dict["resolution"] = []
    _dict["encode_tasks"] = []
    _dict["updated_at"] = datetime.datetime.today().isoformat()
    # jsonの書き込み
    if write_json(json_file, _dict):
        return True
    return False


def update_json(year, cid, vid, title, explanation):
    # 既存のjsonを読み込み
    json_file = "/".join([video_dir, str(year), cid, vid, "info.json"])
    _dict = read_json(json_file)
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
            with open(json_file) as f:
                _dict = await async_wrap(json.load)(f)
        except FileNotFoundError:
            pass
        result[link_path.split("/")[-1]] = _dict
    return result


def result_encode(folderpath, resolution, result=True):
    _list = {
        240: [
            "#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=426x240",
            "240p.m3u8"],
        360: [
            "#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=640x360",
            "360p.m3u8"],
        480: [
            "#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=854x480",
            "480p.m3u8"],
        720: [
            "#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1280x720",
            "720p.m3u8"],
        1080: [
            "#EXT-X-STREAM-INF:BANDWIDTH=8000000,RESOLUTION=1920x1080",
            "1080p.m3u8"],
    }
    # 既存のjsonを読み込み
    json_file = "/".join([folderpath, "info.json"])
    _dict = read_json(json_file)
    if not _dict:
        return False
    if result:
        playlist = "/".join([folderpath, "playlist.m3u8"])
        write_playlist(playlist, _list[int(resolution)], add=True)
        # 画質の追加
        _dict["resolution"].append(f"{resolution}p")
        _dict["encode_tasks"].remove(f"{resolution}p")
    else:
        _dict["encode_error"].append(f"{resolution}p")
        _dict["encode_tasks"].remove(f"{resolution}p")
    # 重複の削除
    _dict["encode_tasks"] = list(set(_dict["encode_tasks"]))
    _dict["resolution"] = list(set(_dict["resolution"]))
    _dict["encode_error"] = list(set(_dict["encode_error"]))
    # jsonの書き込み
    if write_json(json_file, _dict):
        return True
    return False


def add_encode_task(folderpath, resolution):
    # 既存のjsonを読み込み
    json_file = "/".join([folderpath, "info.json"])
    _dict = read_json(json_file)
    if not _dict:
        return False
    if f"{resolution}p" in _dict["resolution"]:
        return True
    # 画質の追加
    _dict["encode_tasks"].append(f"{resolution}p")
    # 重複の削除
    _dict["encode_tasks"] = list(set(_dict["encode_tasks"]))
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
        temp = await async_wrap(read_json)(json_file)
        for i in temp["encode_tasks"]:
            if i in temp["resolution"]:
                temp["encode_tasks"].remove(i)
        write_json(json_file, temp)

        directory = "/".join(json_file.split("/")[:-1])
        temp["video_directory"] = directory
        temp["video_file_name"] = glob.glob(
            f"{directory}/1.*")[0].split("/")[-1]
        result.append(temp)
    return result


async def get_encode_tasks():
    video_info = await get_all_info()
    result = []
    for info in video_info:
        if len(info["encode_tasks"]) > 0:
            result.append(info)
    return result
