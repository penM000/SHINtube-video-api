from ..command_run import command_run
import time


async def encode(folderpath: str, filename: str, width=1920, height=1080) -> bool:
    temp = filename.split(".")[:-2]
    await command_run("ls", "./bin/")
    await command_run("chmod +x ffmpeg", "./bin/")

    # await command_run(f"./bin/ffmpeg -i {folderpath}/{filename} -codec: copy
    # -start_number 0 -hls_time 10 -hls_list_size 0 -f hls
    # {folderpath}/{filename}.m3u8 ", "./")
    now = time.time()
    await command_run(
        f"./bin/ffmpeg -i {folderpath}/{filename} \
            -crf 20 -start_number 0 -hls_time 10 \
                -hls_list_size 0 -f hls {folderpath}/{filename}.m3u8 ", "./")
    print(time.time() - now)
