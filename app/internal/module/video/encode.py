from ..command_run import command_run
import logging
logger = logging.getLogger('uvicorn')

bitrate_dict = {
    1080: 12,
    720: 7.5,
    480: 4,
    360: 1.5,
    240: 1,
    160: 1
}


async def soft_encode(folderpath: str, filename: str, width=1920, height=1080, thread=1) -> bool:
    command = [
        "ffmpeg",
        "-y",
        f"-threads {thread}",
        f"-i {folderpath}/{filename}",
        f"-threads {thread}",
        "-vcodec libx264",
        # f"-progress {folderpath}/progress.txt",
        "-crf 20",
        "-start_number 0",
        "-hls_time 6",
        "-hls_list_size 0",
        "-f hls",
        # f"-s {width}x{height}",
        f"-vf fps=30,scale=-2:{height}",
        f"{folderpath}/{height}p.m3u8"
    ]
    result = await command_run(" ".join(command), "./")
    if result.returncode == 0:
        return True
    else:
        logger.error("software encoder error")
        logger.error(" ".join(command))
        logger.error(result.stdout)
        logger.error(result.stderr)
        return False


async def vaapi_encode(folderpath: str, filename: str, width=1920, height=1080) -> bool:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-init_hw_device vaapi=intel:/dev/dri/renderD128",
        "-hwaccel vaapi",
        "-hwaccel_output_format vaapi",
        "-hwaccel_device intel",
        "-filter_hw_device intel",
        f"-i {folderpath}/{filename}",
        "-vcodec h264_vaapi",
        f"-vf 'format=nv12|vaapi,hwupload,fps=30,scale_vaapi=w=-2:h={height}'",
        "-profile high",
        "-compression_level 0",
        "-start_number 0",
        f"-b:v {bitrate_dict[height]}M",
        "-rc_mode VBR",
        "-hls_time 6",
        "-hls_list_size 0",
        "-f hls",
        f"{folderpath}/{height}p.m3u8"
    ]
    result = await command_run(" ".join(command), "./")
    if result.returncode == 0:
        return True
    else:
        logger.error("vaapi encoder error")
        logger.error(" ".join(command))
        logger.error(result.stdout)
        logger.error(result.stderr)
        return False


async def nvenc_encode(folderpath: str, filename: str, width=1920, height=1080,
                       hw_decode=True) -> bool:
    if hw_decode:
        command = [
            "/opt/bin/ffmpeg",
            "-hide_banner",
            "-y",
            "-vsync 0",
            "-hwaccel cuda",
            "-hwaccel_output_format cuda",
            f"-i {folderpath}/{filename}",
            "-b:a 192k",
            "-aac_coder twoloop",
            "-c:v h264_nvenc",
            "-preset medium",
            "-profile:v high",
            "-bf 3",
            "-b_ref_mode 2",
            "-temporal-aq 1",
            f"-vf scale_cuda=-2:{height}",
            f"-b:v {bitrate_dict[height]}M",
            f"-bufsize {bitrate_dict[height]*2}M",
            "-hls_time 6",
            "-hls_list_size 0",
            "-f hls",
            f"{folderpath}/{height}p.m3u8"
        ]
    else:
        command = [
            "/opt/bin/ffmpeg",
            "-hide_banner",
            "-y",
            "-vsync 0",
            "-init_hw_device cuda"
            "-hwaccel_output_format cuda",
            f"-i {folderpath}/{filename}",
            "-b:a 192k",
            "-aac_coder twoloop",
            "-c:v h264_nvenc",
            "-preset medium",
            "-profile:v high",
            "-bf 3",
            "-b_ref_mode 2",
            "-temporal-aq 1",
            f"-vf hwupload,scale_cuda=-2:{height}",
            f"-b:v {bitrate_dict[height]}M",
            f"-bufsize {bitrate_dict[height]*2}M",
            "-hls_time 6",
            "-hls_list_size 0",
            "-f hls",
            f"{folderpath}/{height}p.m3u8"
        ]
    result = await command_run(" ".join(command), "./")
    if result.returncode == 0:
        return True
    else:
        logger.error("nvenc encoder error")
        logger.error(" ".join(command))
        logger.error(result.stdout)
        logger.error(result.stderr)
        return False


async def thumbnail(folderpath: str, filename: str) -> bool:
    command = [
        "ffmpeg",
        "-y",
        f"-i {folderpath}/{filename}",
        "-ss 5",
        "-vframes 1",
        "-f image2",
        # f"-s {width}x{height}",
        "-vf scale=-2:360",
        f"{folderpath}/thumbnail_360.jpg"
    ]
    await command_run(" ".join(command), "./")
    command = [
        "ffmpeg",
        "-y",
        f"-i {folderpath}/{filename}",
        "-ss 5",
        "-vframes 1",
        "-f image2",
        # f"-s {width}x{height}",
        "-vf scale=-2:720",
        f"{folderpath}/thumbnail_720.jpg"
    ]
    await command_run(" ".join(command), "./")


async def get_video_resolution(folderpath: str, filename: str) -> dict:
    command = [
        "ffprobe",
        "-v error",
        "-select_streams v:0",
        "-show_entries stream=width,height",
        "-of csv=s=x:p=0",
        f"{folderpath}/{filename}",
    ]
    result = await command_run(" ".join(command), "./")
    try:
        return {"width": int(result.stdout.split("x")[0]),
                "height": int(result.stdout.split("x")[1])}
    except Exception:
        return False


async def encode_test():
    folderpath = "sample"
    filename = "video.mp4"
    result = {}
    if await vaapi_encode(folderpath, filename):
        result["vaapi"] = True
    else:
        result["vaapi"] = False

    if await nvenc_encode(folderpath, filename) and \
            await nvenc_encode(folderpath, filename, hw_decode=False):
        result["nvenc"] = True
        result["vaapi"] = False
    else:
        result["nvenc"] = False

    if result["vaapi"] or result["nvenc"]:
        result["soft"] = False
    else:
        result["soft"] = True
    return result
