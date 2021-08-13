from ..command_run import command_run
from .item import add_resolution
import time


async def encode(folderpath: str, filename: str, width=1920, height=1080, thread=1) -> bool:
    await command_run("chmod +x ffmpeg", "./bin/")
    now = time.time()
    command = [
        "./bin/ffmpeg",
        "-y",
        f"-threads {thread}",
        f"-i {folderpath}/{filename}",
        f"-threads {thread}",
        "-vcodec libx264",
        # f"-progress {folderpath}/progress.txt",
        "-crf 20",
        "-start_number 0",
        "-hls_time 10",
        "-hls_list_size 0",
        "-f hls",
        # f"-s {width}x{height}",
        f"-vf scale=-1:{height}",
        f"{folderpath}/{height}p.m3u8"
    ]
    await command_run(" ".join(command), "./")
    add_resolution(folderpath, f"{height}p")
    await thumbnail(folderpath, filename)
    print(time.time() - now)


async def thumbnail(folderpath: str, filename: str) -> bool:
    await command_run("chmod +x ffmpeg", "./bin/")
    command = [
        "./bin/ffmpeg",
        "-y",
        f"-i {folderpath}/{filename}",
        "-ss 5",
        "-vframes 1",
        "-f image2",
        # f"-s {width}x{height}",
        "-vf scale=-1:360",
        f"{folderpath}/thumbnail_360.jpg"
    ]
    await command_run(" ".join(command), "./")
    command = [
        "./bin/ffmpeg",
        f"-i {folderpath}/{filename}",
        "-ss 5",
        "-vframes 1",
        "-f image2",
        # f"-s {width}x{height}",
        "-vf scale=-1:720",
        f"{folderpath}/thumbnail_720.jpg"
    ]
    await command_run(" ".join(command), "./")
