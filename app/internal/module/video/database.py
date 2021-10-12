import glob
import pathlib
from .filemanager import filemanager_class


class database_class(filemanager_class):
    def __init__(self):
        filemanager_class.__init__(self)

    async def update_info(self, year, cid, vid, title, explanation, meta_data):
        # 既存のjsonを読み込み
        json_file = "/".join([self.video_dir, str(year),
                             cid, vid, "info.json"])
        _dict = await self.read_json(json_file)
        if not _dict:
            return False
        # jsonの更新
        _dict["title"] = title
        _dict["explanation"] = explanation
        _dict["meta_data"] = meta_data
        # jsonの書き込み
        if self.write_json(json_file, _dict):
            return True
        return False

    async def encode_result(self, folderpath, resolution, result=True):
        # 既存のjsonを読み込み
        json_file = "/".join([folderpath, "info.json"])
        _dict = await self.read_json(json_file)

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
        self.write_json(json_file, _dict)
        # プレイリストに書き込み
        playlist = "/".join([folderpath, "playlist.m3u8"])
        await self.write_playlist(playlist, resolution)

    async def encode_task(self, folderpath, resolution):
        # 既存のjsonを読み込み
        json_file = "/".join([folderpath, "info.json"])
        _dict = await self.read_json(json_file)
        if not _dict:
            return False
        if f"{resolution}p" in _dict["resolution"]:
            return True
        # 画質の追加
        _dict["encode_tasks"].append(f"{resolution}p")
        # jsonの書き込み
        if self.write_json(json_file, _dict):
            return True
        return False

    async def encode_error(self, folderpath, message):
        # 既存のjsonを読み込み
        json_file = "/".join([folderpath, "info.json"])
        _dict = await self.read_json(json_file)
        if not _dict:
            return False
        # 画質の追加
        _dict["encode_error"].append(f"{message}")
        # jsonの書き込み
        if self.write_json(json_file, _dict):
            return True
        return False

    async def get_all_info(self):
        json_files_path = await self.async_wrap(glob.glob)(
            f"./{self.video_dir}/**/info.json",
            recursive=True)
        result = []
        for json_file in json_files_path:
            temp = await self.read_json(json_file)

            directory = "/".join(json_file.split("/")[:-1])
            temp["video_directory"] = directory
            try:
                temp["video_file_name"] = glob.glob(
                    f"{directory}/1.*")[0].split("/")[-1]
            except IndexError:
                temp["video_file_name"] = None
            result.append(temp)
        return result

    async def get_encode_tasks(self):
        video_info = await self.get_all_info()
        result = []
        for info in video_info:
            if len(info["encode_tasks"]) > 0:
                result.append(info)
        return result

    async def list_video_id(self, year, cid):
        _video_dir = "/".join([self.video_dir, str(year), cid])
        temp = await self.async_wrap(glob.glob)(f"{_video_dir}/*")
        return [video_id.split("/")[-1]
                for video_id in temp]

    async def list_link(self, year, cid):
        _video_dir = "/".join([self.video_dir, str(year), cid])
        temp = await self.async_wrap(glob.glob)(f"{_video_dir}/*")
        result = {}
        for link_path in temp:
            json_file = link_path + "/info.json"
            _dict = await self.read_json(json_file)
            if not _dict:
                pass
            else:
                result[link_path.split("/")[-1]] = _dict
        return result

    async def get_all_info(self):
        json_files_path = await self.async_wrap(glob.glob)(
            f"./{self.video_dir}/**/info.json",
            recursive=True)
        result = []
        for json_file in json_files_path:
            temp = await self.read_json(json_file)

            directory = "/".join(json_file.split("/")[:-1])
            temp["video_directory"] = directory
            try:
                temp["video_file_name"] = glob.glob(
                    f"{directory}/1.*")[0].split("/")[-1]
            except IndexError:
                temp["video_file_name"] = None
            result.append(temp)
        return result

    async def get_encode_tasks(self):
        video_info = await self.get_all_info()
        result = []
        for info in video_info:
            if len(info["encode_tasks"]) > 0:
                result.append(info)
        return result


database = database_class()
