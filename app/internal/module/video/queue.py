import asyncio
import multiprocessing
from dataclasses import dataclass, field
from typing import Any

from .encode import (
    soft_encode,
    vaapi_encode,
    nvenc_encode,
    get_video_resolution,
    thumbnail,
    encode_test)
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
        await result_encode(
            encode_config["folderpath"],
            encode_config["height"],
            result)

        # DBにdoneの更新
        queue.task_done()


async def nvenc_encode_worker(queue: QueueItem):
    while True:
        # Get a "work item" out of the queue.
        queue_item = await queue.get()
        encode_config = queue_item.item
        # DBにprogressの更新

        result = await nvenc_encode(
            folderpath=encode_config["folderpath"],
            filename=encode_config["filename"],
            height=encode_config["height"]
        )
        await result_encode(
            encode_config["folderpath"],
            encode_config["height"],
            result)

        # DBにdoneの更新
        queue.task_done()


async def soft_and_nvenc_encode_worker(queue: QueueItem):
    while True:
        # Get a "work item" out of the queue.
        queue_item = await queue.get()
        encode_config = queue_item.item
        # DBにprogressの更新

        result = await nvenc_encode(
            folderpath=encode_config["folderpath"],
            filename=encode_config["filename"],
            height=encode_config["height"],
            hw_decode=False
        )
        await result_encode(
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
            thread=int(multiprocessing.cpu_count()) - 2
        )
        await result_encode(
            encode_config["folderpath"],
            encode_config["height"],
            result)

        # DBにdoneの更新
        queue.task_done()


async def add_encode_queue(folderpath, filename, encode_resolution="Auto"):
    global queue
    global encode_workers
    if queue is None:
        queue = asyncio.PriorityQueue()
        result = await encode_test()
        if result["vaapi"]:
            task = asyncio.create_task(vaapi_encode_worker(queue))
            encode_tasks.append(task)
        if result["nvenc"]:
            task = asyncio.create_task(nvenc_encode_worker(queue))
            encode_tasks.append(task)
            task = asyncio.create_task(soft_and_nvenc_encode_worker(queue))
            encode_tasks.append(task)
        if result["soft"]:
            task = asyncio.create_task(soft_encode_worker(queue))
            encode_tasks.append(task)
    # 動画の形式確認
    input_video_resolution = await get_video_resolution(folderpath, filename)
    # print(input_video_resolution)
    if not isinstance(input_video_resolution, dict):
        await add_encode_task(folderpath, 1080)
        await result_encode(folderpath, 1080, False)
        return

    if encode_resolution == "Auto":
        video_size = [240, 360, 480, 720, 1080]
        for height in video_size:
            if input_video_resolution["height"] >= height:
                encode_config = {
                    "folderpath": folderpath,
                    "filename": filename,
                    "height": height
                }
                queue_item = QueueItem(priority=height, item=encode_config)
                queue.put_nowait(queue_item)
                await add_encode_task(folderpath, height)
    else:
        height = int(encode_resolution)
        encode_config = {
            "folderpath": folderpath,
            "filename": filename,
            "height": height
        }
        queue_item = QueueItem(priority=height, item=encode_config)
        queue.put_nowait(queue_item)
        await add_encode_task(folderpath, height)
    await thumbnail(folderpath, filename)
