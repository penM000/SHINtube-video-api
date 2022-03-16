
import asyncio
import pathlib
import shutil

from ..module.general_module import general_module
from .filemanager import FilemanagerClass


class FilecopyClass(FilemanagerClass):

    def __init__(self):
        pass

    async def copy_video_lock(self,
                              src_path,
                              dst_path):
        # コピーモードのロックをかける
        # コピー元
        src_folder_path = pathlib.Path(str(src_path))
        src_info_path = src_folder_path / "info.json"
        src_info = general_module.read_json_sync(src_info_path)
        # info.jsonにstatusキーがないときの処理
        if "status" in src_info:
            src_info["status"].append("copying")
        else:
            src_info["status"] = ["copying"]
        general_module.write_json(src_info_path, src_info)

        # コピー先
        dst_folder_path = pathlib.Path(str(dst_path))
        # 既にコピー先がある場合は削除
        if dst_folder_path.exists():
            await general_module.async_wrap(shutil.rmtree)(dst_folder_path)
        # コピー先のディレクトリを作成
        await self.create_directory(dst_folder_path)
        (dst_folder_path.parent.parent / "automatic_created_dir").touch()
        dst_info_path = dst_folder_path / "info.json"
        general_module.write_json(dst_info_path, src_info)
        # コピー中断時に復旧するためのマーカ設置
        copy_maker_path = dst_folder_path / "automatic_copy_maker"
        with copy_maker_path.open(mode='w') as f:
            f.write(f'{src_path}\n{dst_path}')
        return

    async def copy_video_unlock(self,
                                src_path,
                                dst_path):
        # コピーモードのロックを解除
        # コピー元
        src_folder_path = pathlib.Path(str(src_path))
        src_info_path = src_folder_path / "info.json"
        src_info = general_module.read_json_sync(src_info_path)
        # ロックの解除
        src_info["status"] = list(set(src_info["status"]))
        src_info["status"].remove("copying")

        general_module.write_json(src_info_path, src_info)

        # コピー先
        dst_folder_path = pathlib.Path(str(dst_path))
        dst_info_path = dst_folder_path / "info.json"
        general_module.write_json(dst_info_path, src_info)
        # コピー中断時に復旧するためのマーカ削除
        copy_maker_path = dst_folder_path / "automatic_copy_maker"
        copy_maker_path.unlink()
        return

    async def copy_video_backend(self, src_path, dst_path):
        # コピーの実行
        await general_module.async_wrap(shutil.copytree)(src_path,
                                                         dst_path,
                                                         dirs_exist_ok=True)
        # コピーロックの解除
        await self.copy_video_unlock(src_path, dst_path)

    async def copy_video(self,
                         src_service_name,
                         src_cid,
                         src_vid,
                         dst_service_name,
                         dst_cid,
                         dst_vid=None):
        src_path = "/".join([self.video_dir,
                             src_service_name,
                             src_cid, src_vid])

        if dst_vid is None:
            dst_vid = src_vid

        dst_path = "/".join([self.video_dir,
                             dst_service_name,
                             dst_cid, dst_vid])
        if src_path == dst_path:
            return
        # コピーモードのロックをかける
        await self.copy_video_lock(src_path, dst_path)
        asyncio.create_task(self.copy_video_backend(src_path, dst_path))

    async def copy_cid_directory(self,
                                 src_service_name,
                                 src_cid,
                                 dst_service_name,
                                 dst_cid,):
        src_path = "/".join([self.video_dir,
                             src_service_name,
                             src_cid])
        directories = await self.directory_list(src_path)
        for directory in directories:
            # info.jsonがあるものだけコピー対象
            info_json = directory / "info.json"
            if info_json.exists():
                src_vid = str(directory.name)

                await self.copy_video(src_service_name,
                                      src_cid,
                                      src_vid,
                                      dst_service_name,
                                      dst_cid)

        pass
