from concurrent.futures import ThreadPoolExecutor
import pathlib


import json

import glob
import aiofiles

import asyncio
from functools import wraps, partial


# 保存先のビデオフォルダ
video_dir = "video"


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


def audio_recovery():
    video_path = pathlib.Path("./")
    audio_files_path = video_path.glob(
        f"./{video_dir}/**/audio.m3u8")
    for i in audio_files_path:
        done_file_path = i.parent / "audio.done"
        if not done_file_path.exists():
            i.unlink()
