import asyncio

from dataclasses import dataclass, field
from typing import Any, List, Union

from .encode import encoder
from .database import database
from ..module.logger import logger


class Queue_Class:

    def __init__(self):
        self.PriorityQueue = None
        self.encode_workers: List[asyncio.Task] = []

    @dataclass(order=True)
    class QueueItem:
        priority: int
        item: Any = field(compare=False)

    async def encode_worker(self, queue: asyncio.PriorityQueue):
        """
        エンコードを実行するワーカー関数
        """
        while True:
            queue_item = await queue.get()
            encode_config = queue_item.item

            result = await encoder.encode(
                folderpath=encode_config["folderpath"],
                filename=encode_config["filename"],
                resolution=encode_config["resolution"])

            await database.encode_result(encode_config["folderpath"],
                                         encode_config["resolution"],
                                         result)
            queue.task_done()

    def create_encode_worker(self):
        for task in self.encode_workers:
            task.cancel()
        self.PriorityQueue = asyncio.PriorityQueue()
        for i in range(2):
            task = asyncio.create_task(self.encode_worker(self.PriorityQueue))
            self.encode_workers.append(task)

    async def check_original_video(self,
                                   folderpath: str,
                                   filename: str) -> bool:
        folderpath, filename = str(folderpath), str(filename)
        # 動画の形式確認
        input_video_info = await encoder.get_video_info(folderpath, filename)
        # 映像がなければエラー
        if not input_video_info.is_video:
            logger.warning(f"{folderpath} not video file")
            await database.encode_error(folderpath, "not video file")
            return False
        else:
            return True

    async def add_encode_queue(self,
                               folderpath: str,
                               filename: str,
                               resolution: int):
        folderpath, filename = str(folderpath), str(filename)
        resolution = int(resolution)

        await database.encode_task(folderpath, resolution)
        encode_config = {
            "folderpath": folderpath,
            "filename": filename,
            "resolution": resolution
        }
        queue_item = self.QueueItem(priority=resolution, item=encode_config)
        self.PriorityQueue.put_nowait(queue_item)

    async def add_original_video(self,
                                 folderpath: str,
                                 filename: str,
                                 encode_resolution="Auto"):
        if self.PriorityQueue is None:
            self.create_encode_worker()

        if self.check_original_video(folderpath, filename):
            await encoder.thumbnail(folderpath, filename)
        else:
            return False

        input_video_info = await encoder.get_video_info(folderpath, filename)
        if encode_resolution == "Auto":
            video_resolution = [360, 480, 720, 1080]
            for resolution in video_resolution:
                # 入力解像度が超えていれば追加
                if input_video_info.height >= resolution or resolution == 360:
                    await self.add_encode_queue(folderpath,
                                                filename,
                                                resolution)
            pass
        else:
            resolution = int(encode_resolution)
            await self.add_encode_queue(folderpath,
                                        filename,
                                        resolution)


queue = Queue_Class()
