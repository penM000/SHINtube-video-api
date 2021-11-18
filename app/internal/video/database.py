import glob
import pathlib
from ..module.general_module import general_module
from .filemanager import FilemanagerClass


class DatabaseClass(FilemanagerClass):
    def __init__(self):
        FilemanagerClass.__init__(self)

    async def update_info(self,
                          service_name,
                          cid,
                          vid,
                          title,
                          explanation,
                          meta_data):
        # 既存のjsonを読み込み
        json_file = "/".join([self.video_dir, service_name,
                             cid, vid, "info.json"])
        _dict = await general_module.read_json(json_file)
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
        _dict = await general_module.read_json(json_file)

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
        _dict = await general_module.read_json(json_file)
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
        _dict = await general_module.read_json(json_file)
        if not _dict:
            return False
        # 画質の追加
        _dict["encode_error"].append(f"{message}")
        # jsonの書き込み
        if self.write_json(json_file, _dict):
            return True
        return False

    async def list_video_id(self, service_name, cid):
        _video_dir = "/".join([self.video_dir, service_name, cid])
        temp = await general_module.async_wrap(glob.glob)(f"{_video_dir}/*")
        return [video_id.split("/")[-1]
                for video_id in temp]

    async def list_link(self, service_name, cid):
        """
        cidフォルダ内のvidのinfo.jsonをすべて取得
        """
        async_list = general_module.async_wrap(list)
        cid_path_str = "/".join([self.video_dir, service_name, cid])
        cid_path = pathlib.Path(cid_path_str)
        info_json_paths = await async_list(cid_path.glob("*/info.json"))
        result = {}
        for info_json_path in info_json_paths:
            json_data = await general_module.read_json(info_json_path)
            vid = info_json_path.parent.name
            result[vid] = json_data
        return result

    async def get_all_info(self):
        """
        videoフォルダ上に存在するすべてのinfo.jsonの取得
        """
        async_list = general_module.async_wrap(list)
        video_path = pathlib.Path(self.video_dir)
        info_json_paths = await async_list(video_path.glob("**/info.json"))
        result = []
        for info_json_path in info_json_paths:
            info_json_data = await general_module.read_json(info_json_path)
            if info_json_data:
                info_json_data["video_directory"] = str(info_json_path.parent)
                input_video = list(
                    info_json_path.parent.glob("original_video.*"))
                if input_video:
                    info_json_data["video_file_name"] = input_video[0].name
                else:
                    info_json_data["video_file_name"] = None
                result.append(info_json_data)
        return result

    async def get_encode_tasks(self):
        video_info = await self.get_all_info()
        result = []
        for info in video_info:
            if len(info["encode_tasks"]) > 0:
                result.append(info)
        return result


database = DatabaseClass()
