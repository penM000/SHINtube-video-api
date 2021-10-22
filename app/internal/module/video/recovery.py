import pathlib
import asyncio
from .encode import encoder
from .database import database
from .filemanager import filemanager
from .queue import add_encode_queue
from ..logger import logger
video_dir = "video"


class recovery_class():
    def audio_recovery(self):
        # info.jsonが存在するパスを取得
        video_path = pathlib.Path("./")
        info_paths = video_path.glob("**/info.json")
        for info_path in info_paths:
            done_file_path = info_path.parent / "audio.done"
            # audio.doneの存在を確認
            if not done_file_path.exists():
                audio_m3u8_path = info_path.parent / "audio.m3u8"
                # audioエンコードが中断されている場合は初期化
                if audio_m3u8_path.exists():
                    audio_m3u8_path.unlink()
                # audioのエンコードを実行
                try:
                    input_video_file = list(info_path.parent.glob("1.*"))[0]
                    asyncio.create_task(
                        encoder.encode_audio(
                            str(info_path.parent), input_video_file.name))
                except Exception:
                    pass

    async def file_recovery(self):
        # info.jsonが存在するパスを取得
        info_paths = pathlib.Path("./").glob("**/info.json")
        for info_path in info_paths:
            done_file_path = info_path.parent / "file.done"
            # file.doneの存在を確認
            if not done_file_path.exists():
                # POSTされたファイルが受け取れなかった場合エラー
                logger.warning(f"file write error {info_path.parent}")
                await database.encode_error(str(info_path.parent),
                                            "file write error")
            # info.jsonを取得
            info_data = await filemanager.read_json(info_path)
            count = 0
            # info.jsonのリストの要素がすべて0なら初期状態
            for key in info_data:
                if isinstance(info_data[key], list):
                    count += len(info_data[key])
            # info.jsonが初期状態の場合
            if count == 0:
                # エンコードタスクに追加
                try:
                    video_file_path = list(info_path.parent.glob("1.*"))[0]
                    await add_encode_queue(str(video_file_path.parent),
                                           str(video_file_path.name))
                except Exception:
                    pass

    async def encode_recovery(self):
        # エンコード中で強制終了されたタスクを取得
        tasks = await database.get_encode_tasks()
        for task in tasks:
            for encode_resolution in task["encode_tasks"]:
                # 1080pを1080に変換
                resolution = int(encode_resolution[:-1])
                # 解像度を指定してエンコードタスクに追加
                await add_encode_queue(folderpath=task["video_directory"],
                                       filename=task["video_file_name"],
                                       encode_resolution=resolution)

    async def runrecovery(self):
        # audio_recoveryは最優先で実行
        self.audio_recovery()
        await self.file_recovery()
        await self.encode_recovery()


recovery = recovery_class()
