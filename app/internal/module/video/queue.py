import asyncio
from dataclasses import dataclass, field
from typing import Any

from .encode import encode, get_video_resolution
from .item import add_resolution_task


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

        # DBにdoneの更新
        queue.task_done()


async def add_encode_queue(folderpath, filename, height):
    global queue
    global encode_workers
    if queue is None:
        queue = asyncio.PriorityQueue()
        for i in range(1):
            task = asyncio.create_task(encode_worker(queue))
            encode_tasks.append(task)
    encode_config = {
        "folderpath": folderpath,
        "filename": filename,
        "height": height
    }
    # DBにwaitで登録
    await get_video_resolution(folderpath, filename)
    add_resolution_task(folderpath, height)
    queue_item = QueueItem(priority=height, item=encode_config)

    queue.put_nowait(queue_item)
