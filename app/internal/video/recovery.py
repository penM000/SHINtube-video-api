import asyncio
import pathlib
from typing import List, Union

from .encode import encoder
from .database import database
from ..module.general_module import general_module
from .queue import queue
from .filecopy import FilecopyClass
from ..module.logger import logger


class recovery_class():

    async def get_all_info_path(self) -> List[pathlib.PosixPath]:
        async_list = general_module.async_wrap(list)
        current_directory = pathlib.Path("./")
        info_paths = current_directory.glob("**/info.json")
        info_paths = await async_list(info_paths)
        return info_paths

    async def get_original_video_path(self,
                                      video_content_path: pathlib.PosixPath
                                      ) -> Union[pathlib.PosixPath, None]:
        async_list = general_module.async_wrap(list)
        # original_video.拡張子のパスを取得
        temp = video_content_path.glob("**/original_video.*")
        temp = await async_list(temp)
        if temp:
            original_video_path = temp[0]
        else:
            original_video_path = None
        return original_video_path

    async def encode_queue_recovery(self,
                                    info_path: pathlib.PosixPath) -> None:
        video_content_path = info_path.parent

        # info.jsonを取得
        info_data = await general_module.read_json_async(info_path)
        count = 0

        # info.jsonのリストの要素がすべて0なら初期状態
        for key in info_data:
            if isinstance(info_data[key], list):
                count += len(info_data[key])

        # original_video.拡張子のパスを取得
        original_video_path = await self.get_original_video_path(
            video_content_path)

        # info.jsonが初期状態の場合
        if count == 0 and original_video_path is not None:
            video_file_path = original_video_path
            await queue.add_original_video(str(video_file_path.parent),
                                           str(video_file_path.name))

    async def encode_video_recovery(self, info_path: pathlib.PosixPath):
        video_content_path = info_path.parent

        # info.jsonの読み取り
        info_data = await general_module.read_json_async(info_path)
        # original_video.拡張子のパスを取得
        original_video_path = await self.get_original_video_path(
            video_content_path)

        # エンコードタスクが残っている場合
        for encode_resolution in info_data["encode_tasks"]:
            if original_video_path is not None:
                resolution = int(encode_resolution[:-1])
                await queue.add_original_video(
                    folderpath=video_content_path,
                    filename=original_video_path.name,
                    encode_resolution=resolution)

    async def encode_audio_recovery(self, info_path: pathlib.PosixPath):
        video_content_path = info_path.parent
        audio_done_path = video_content_path / "audio.done"
        audio_m3u8_path = video_content_path / "audio.m3u8"
        # original_video.拡張子のパスを取得
        original_video_path = await self.get_original_video_path(
            video_content_path)
        # audio.doneもしくは、audio.m3u8が存在しないとき
        if not audio_done_path.exists() or not audio_m3u8_path.exists():
            # original_video_pathが存在するとき
            if original_video_path is not None:
                # 音声エンコードを実行
                encode_task = encoder.encode_audio(
                    str(info_path.parent), original_video_path.name)
                asyncio.create_task(encode_task)

    async def directory_recovery(self, info_path: pathlib.PosixPath) -> None:
        video_content_path = info_path.parent
        # emptyfileは見ない
        if (video_content_path / "emptyfile").exists():
            return

        # audioの整合性チェック
        audio_done_path = video_content_path / "audio.done"
        audio_m3u8_path = video_content_path / "audio.m3u8"
        # 正常に音声エンコードが完了している場合
        if audio_done_path.exists():
            pass
        # 音声エンコードが途中の場合
        elif audio_m3u8_path.exists():
            audio_m3u8_path.unlink()

        # original_videoの整合性チェック
        file_done_path = video_content_path / "file.done"
        # 正常にアップロードファイルが処理されている場合
        if file_done_path.exists():
            pass
        # 正常にアップロードファイルが処理されなかった場合
        else:
            logger.warning(f"file write error {str(video_content_path)}")
            await database.encode_error(str(video_content_path),
                                        "file write error")

    async def copy_recovery(self):
        async_list = general_module.async_wrap(list)
        current_directory = pathlib.Path("./")
        copy_maker_paths = current_directory.glob("**/automatic_copy_maker")
        copy_maker_paths = await async_list(copy_maker_paths)
        filecopy = FilecopyClass()
        for copy_maker_path in copy_maker_paths:
            copy_maker_data = await general_module.read_file(copy_maker_path)
            src_path = copy_maker_data.split("\n")[0]
            dst_path = copy_maker_data.split("\n")[-1]

            asyncio.create_task(
                filecopy.copy_video_backend(
                    src_path, dst_path))

        pass

    async def runrecovery(self):
        info_paths = await self.get_all_info_path()
        for info_path in info_paths:
            # 実行順に依存関係あり
            # video -> queue
            # directory -> audio
            # そうしないとqueueで追加されたものをvideoでもエンコードしてしまう
            await self.directory_recovery(info_path)
            await self.encode_video_recovery(info_path)
            await self.encode_queue_recovery(info_path)
            await self.encode_audio_recovery(info_path)
        await self.copy_recovery()


recovery = recovery_class()
