import asyncio
import multiprocessing
from dataclasses import dataclass, field
from typing import Any

from .encode import soft_encode, vaapi_encode, get_video_resolution, thumbnail
from .item import result_encode, add_encode_task


@dataclass(order=True)
class QueueItem:
    """
    キューアイテム
    """
    priority: int
    item: Any = field(compare=False)


queue = None
encode_tasks = []


async def vaapi_encode_worker(queue: QueueItem):
    while True:
        # Get a "work item" out of the queue.
        queue_item = await queue.get()
        encode_config = queue_item.item
        # DBにprogressの更新

        result = await vaapi_encode(
            folderpath=encode_config["folderpath"],
            filename=encode_config["filename"],
            height=encode_config["height"]
        )
        result_encode(
            encode_config["folderpath"],
            encode_config["height"],
            result)

        # DBにdoneの更新
        queue.task_done()


async def soft_encode_worker(queue: QueueItem):
    while True:
        # Get a "work item" out of the queue.
        queue_item = await queue.get()
        encode_config = queue_item.item
        # DBにprogressの更新

        result = await soft_encode(
            folderpath=encode_config["folderpath"],
            filename=encode_config["filename"],
            height=encode_config["height"],
            thread=int(multiprocessing.cpu_count())-2
        )
        result_encode(
            encode_config["folderpath"],
            encode_config["height"],
            result)

        # DBにdoneの更新
        queue.task_done()


async def add_encode_queue(folderpath, filename):
    global queue
    global encode_workers
    if queue is None:
        queue = asyncio.PriorityQueue()
        for i in range(2):
            task = asyncio.create_task(vaapi_encode_worker(queue))
            encode_tasks.append(task)

    # DBにwaitで登録
    resolution = await get_video_resolution(folderpath, filename)
    if not resolution:
        add_encode_task(folderpath, 1080)
        result_encode(folderpath, 1080, False)
        return
    video_size = [240, 360, 480, 720, 1080]
    # video_size = [240, 360]
    for height in video_size:
        if resolution["height"] >= height:
            encode_config = {
                "folderpath": folderpath,
                "filename": filename,
                "height": height
            }
            queue_item = QueueItem(priority=height, item=encode_config)
            queue.put_nowait(queue_item)
            add_encode_task(folderpath, height)
    await thumbnail(folderpath, filename)
