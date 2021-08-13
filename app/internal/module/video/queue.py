import asyncio

from .encode import encode
from .item import add_resolution_task


queue = None
encode_tasks = []


async def encode_worker(queue):
    while True:
        # Get a "work item" out of the queue.
        height, encode_config = await queue.get()
        print(height)
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
    add_resolution_task(folderpath, f"{height}p")
    queue.put_nowait((height, encode_config))
