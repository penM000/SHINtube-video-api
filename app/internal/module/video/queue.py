import asyncio

from dataclasses import dataclass, field
from typing import Any

from .encode import encoder
from .database import database
from ..logger import logger


@dataclass(order=True)
class QueueItem:
    """
    キューアイテム
    """
    priority: int
    item: Any = field(compare=False)


queue = None
encode_tasks = []


async def encode_worker(queue: QueueItem):
    while True:
        # Get a "work item" out of the queue.
        queue_item = await queue.get()
        encode_config = queue_item.item
        # DBにprogressの更新

        result = await encoder.encode(
            folderpath=encode_config["folderpath"],
            filename=encode_config["filename"],
            resolution=encode_config["height"])

        await database.encode_result(encode_config["folderpath"],
                                     encode_config["height"],
                                     result)

        # 入力動画の削除判定
        # await filemanager.delete_original_video()

        # DBにdoneの更新
        queue.task_done()


async def add_encode_queue(folderpath, filename, encode_resolution="Auto"):
    global queue
    global encode_workers
    if queue is None:
        queue = asyncio.PriorityQueue()
        await encoder.encode_test()
        for i in range(encoder.encode_worker):
            task = asyncio.create_task(encode_worker(queue))
            encode_tasks.append(task)

    # 動画の形式確認
    input_video_info = await encoder.get_video_info(folderpath, filename)
    # 映像がなければエラー
    if not input_video_info.is_video:
        logger.warning(f"{folderpath} not video file")
        await database.encode_error(folderpath, "not video file")
        return
    else:
        await encoder.thumbnail(folderpath, filename)
    # 解像度ごとにエンコードキューを追加
    if encode_resolution == "Auto":
        video_size = [360, 480, 720, 1080]
        for height in video_size:
            # 入力解像度が超えていれば追加
            if input_video_info.height >= height or height == 360:
                await database.encode_task(folderpath, height)
                encode_config = {
                    "folderpath": folderpath,
                    "filename": filename,
                    "height": height
                }
                queue_item = QueueItem(priority=height, item=encode_config)
                queue.put_nowait(queue_item)

    else:
        # エンコードの再追加用
        height = int(encode_resolution)
        await database.encode_task(folderpath, height)
        encode_config = {
            "folderpath": folderpath,
            "filename": filename,
            "height": height
        }
        queue_item = QueueItem(priority=height, item=encode_config)
        queue.put_nowait(queue_item)
