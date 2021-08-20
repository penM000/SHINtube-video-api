import asyncio
from dataclasses import dataclass, field
from typing import Any

from .encode import encode, get_video_resolution, thumbnail
from .item import add_resolution_task, add_resolution


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
        print(queue_item.priority)
        # DBにprogressの更新

        await encode(
            folderpath=encode_config["folderpath"],
            filename=encode_config["filename"],
            height=encode_config["height"]
        )
        add_resolution(encode_config["folderpath"], encode_config["height"])

        # DBにdoneの更新
        queue.task_done()


async def add_encode_queue(folderpath, filename):
    global queue
    global encode_workers
    if queue is None:
        queue = asyncio.PriorityQueue()
        for i in range(1):
            task = asyncio.create_task(encode_worker(queue))
            encode_tasks.append(task)

    # DBにwaitで登録
    resolution = await get_video_resolution(folderpath, filename)
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
            add_resolution_task(folderpath, height)
    await thumbnail(folderpath, filename)
