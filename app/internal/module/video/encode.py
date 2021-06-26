from ..command_run import command_run
import time


async def encode(folderpath: str, filename: str, width=1920, height=1080) -> bool:
    temp = "".join(filename.split(".")[:-1])
    await command_run("chmod +x ffmpeg", "./bin/")
    now = time.time()
    command = [
        "./bin/ffmpeg",
        "-threads 1",
        f"-i {folderpath}/{filename}",
        "-threads 1",
        "-crf 20",
        "-start_number 0",
        "-hls_time 10",
        "-hls_list_size 0",
        "-f hls",
        # f"-s {width}x{height}",
        f"-vf scale=-1:{height}",
        f"{folderpath}/{temp}_{height}p.m3u8"
    ]
    await command_run(" ".join(command), "./")
    print(time.time() - now)
