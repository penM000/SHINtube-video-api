import os
import random
import string
import json
import shutil
# 保存先のビデオフォルダ
video_dir = "video"


def GetRandomStr(num) -> str:
    # 英数字をすべて取得
    dat = string.digits + string.ascii_lowercase + string.ascii_uppercase

    # 英数字からランダムに取得
    return ''.join([random.choice(dat) for i in range(num)])


def create_directory(year, cid, title, explanation) -> str:
    _create_dir = None
    while True:
        try:
            _create_dir = "/".join([video_dir, str(year),
                                   cid, GetRandomStr(10)])
            os.makedirs(_create_dir)
        except FileExistsError:
            pass
        else:
            break
    dict_template = {
        "title": title,
        "explanation": explanation,
        "resolution": [],
        "encode_tasks": []
    }
    with open(_create_dir + "/info.json", "w") as f:
        json.dump(dict_template, f, indent=4)
    return _create_dir


def delete_directory(year, cid, vid):
    _delete_dir = "/".join([video_dir, year, cid, vid])
    shutil.rmtree(_delete_dir)
    return True


def update_json(year, cid, vid, title, explanation):
    # 既存のjsonを読み込み
    json_file = "/".join([video_dir, year, cid, vid, "info.json"])
    try:
        with open(json_file) as f:
            _dict = json.load(f)
    except FileNotFoundError:
        return False
    # jsonの更新
    _dict["title"] = title
    _dict["explanation"] = explanation
    # jsonの書き込み
    with open(json_file) as f:
        json.dump(_dict, f, indent=4)
    return True


def add_resolution(folderpath, resolution):
    # 既存のjsonを読み込み
    json_file = "/".join([folderpath, "info.json"])
    try:
        with open(json_file) as f:
            _dict = json.load(f)
    except FileNotFoundError:
        return False
    # 画質の追加
    _dict["resolution"].append(resolution)
    _dict["encode_tasks"].remove(resolution)
    # jsonの書き込み
    with open(json_file, "w") as f:
        json.dump(_dict, f, indent=4)
    return True


def add_resolution_task(folderpath, resolution):
    # 既存のjsonを読み込み
    json_file = "/".join([folderpath, "info.json"])
    try:
        with open(json_file) as f:
            _dict = json.load(f)
    except FileNotFoundError:
        return False
    # 画質の追加
    _dict["encode_tasks"].append(resolution)
    # jsonの書き込み
    with open(json_file, "w") as f:
        json.dump(_dict, f, indent=4)
    return True
