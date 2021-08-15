from ..command_run import command_run
from .item import add_resolution
import time

bitrate_dict = {
    1080: "8M",
    720: "5M",
    480: "2.5M",
    360: "1M",
    240: "500k",
    160: "500k"
}


async def soft_encode(folderpath: str, filename: str, width=1920, height=1080, thread=1) -> bool:
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
        f"-vf scale=-2:{height}",
        f"{folderpath}/{height}p.m3u8"
    ]
    exit_code = await command_run(" ".join(command), "./")
    print(exit_code)
    add_resolution(folderpath, height)
    await thumbnail(folderpath, filename)
    print(time.time() - now)


async def encode(folderpath: str, filename: str, width=1920, height=1080) -> bool:
    now = time.time()
    command = [
        "ffmpeg",
        "-y",
        "-init_hw_device vaapi=intel:/dev/dri/renderD128",
        "-hwaccel vaapi",
        "-hwaccel_output_format vaapi",
        "-hwaccel_device intel",
        "-filter_hw_device intel",
        f"-i {folderpath}/{filename}",
        "-vcodec h264_vaapi",
        f"-vf 'format=nv12|vaapi,hwupload,scale_vaapi=w=-2:h={height}'",
        "-profile high",
        "-compression_level 0",
        "-start_number 0",
        f"-b:v {bitrate_dict[height]}",
        "-hls_time 10",
        "-hls_list_size 0",
        "-f hls",
        f"{folderpath}/{height}p.m3u8"
    ]
    exit_code = await command_run(" ".join(command), "./")
    print(exit_code)
    add_resolution(folderpath, height)
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
        "-y",
        f"-i {folderpath}/{filename}",
        "-ss 5",
        "-vframes 1",
        "-f image2",
        # f"-s {width}x{height}",
        "-vf scale=-1:720",
        f"{folderpath}/thumbnail_720.jpg"
    ]
    await command_run(" ".join(command), "./")


async def get_video_resolution(folderpath: str, filename: str) -> bool:
    command = [
        "ffprobe",
        "-v error",
        "-select_streams v:0",
        "-show_entries stream=height",
        "-of csv=p=0",
        f"{folderpath}/{filename}",
        f"> {folderpath}/result.txt"
    ]
    await command_run(" ".join(command), "./")
