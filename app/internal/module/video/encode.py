import multiprocessing
from ..command_run import command_run
import logging
import json
import asyncio
from typing import List
logger = logging.getLogger('uvicorn')


class encoder_class:
    def __init__(self):
        # サンプル動画
        self.sample_dir = "./sample"
        self.sample_video = "video.mp4"
        # 解像度:ビットレート(Mbps)
        self.bitrate = {
            1080: 12,
            720: 7.5,
            480: 4,
            360: 1.5,
            240: 1,
            160: 1
        }
        # 利用可能なエンコーダ
        self.encoder_available = {
            "vaapi": False,
            "nvenc_hw_decode": False,
            "nvenc_sw_decode": False,
            "software": False
        }
        # 同時エンコード数
        self.encode_worker = 0
        # 現在利用中のエンコーダ
        self.encoder_used_status = {
            "vaapi": False,
            "nvenc_hw_decode": False,
            "nvenc_sw_decode": False,
            "software": False
        }

    def software_encode_command(
            self,
            folderpath: str,
            filename: str,
            resolution: int,
            thread: int = int(
            multiprocessing.cpu_count())) -> List[str]:
        """
        ソフトウエアエンコード時のコマンド。
        ビットレートの指定はなく、crfによる品質保持のエンコードを行う。
        """
        command = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-vsync 1",
            f"-threads {thread}",
            f"-i {folderpath}/{filename}",
            f"-threads {thread}",
            "-vcodec libx264",
            "-crf 20",
            "-b:a 192k",
            "-aac_coder twoloop",
            "-start_number 0",
            "-hls_time 6",
            "-hls_list_size 0",
            "-f hls",
            f"-vf scale=-2:{resolution}",
            f"{folderpath}/{resolution}p.m3u8"
        ]
        return command

    def vaapi_encode_command(
            self,
            folderpath: str,
            filename: str,
            resolution: int,
            vaapi_device: str = "/dev/dri/renderD128") -> List[str]:
        """
        vaapi(intel)エンコード時のコマンド。
        VBRでのエンコードを行う。
        """
        command = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-vsync 1",
            f"-init_hw_device vaapi=intel:{vaapi_device}",
            "-hwaccel vaapi",
            "-hwaccel_output_format vaapi",
            "-hwaccel_device intel",
            "-filter_hw_device intel",
            f"-i {folderpath}/{filename}",
            "-vcodec h264_vaapi",
            "-rc_mode VBR",
            f"-b:v {self.bitrate[resolution]}M",
            f"-bufsize {self.bitrate[resolution]*2}M",
            "-b:a 192k",
            "-aac_coder twoloop",
            f"-vf 'format=nv12|vaapi,hwupload,scale_vaapi=w=-2:h={resolution}'",
            "-profile high",
            "-compression_level 0",
            "-start_number 0",
            "-hls_time 6",
            "-hls_list_size 0",
            "-f hls",
            f"{folderpath}/{resolution}p.m3u8"]
        return command

    def nvenc_hw_decode_encode_command(
            self,
            folderpath: str,
            filename: str,
            resolution: int,) -> List[str]:
        """
        nvencエンコード時のコマンド。動画のデコードにはHWが利用される。
        VBRでのエンコードを行う。
        エラー対策のため、実際に出力される動画の解像度は-1されている。
        """
        command = [
            "/opt/bin/ffmpeg",
            "-hide_banner",
            "-y",
            "-vsync 0",
            "-hwaccel cuda",
            "-hwaccel_output_format cuda",
            f"-i {folderpath}/{filename}",
            "-c:v h264_nvenc",
            f"-b:v {self.bitrate[resolution]}M",
            f"-bufsize {self.bitrate[resolution]*2}M",
            "-b:a 192k",
            "-aac_coder twoloop",
            "-preset medium",
            "-profile:v high",
            "-bf 3",
            "-b_ref_mode 2",
            "-temporal-aq 1",
            f"-vf scale_cuda=-2:{resolution-1}",
            "-hls_time 6",
            "-hls_list_size 0",
            "-f hls",
            f"{folderpath}/{resolution}p.m3u8",
        ]
        return command

    def nvenc_sw_decode_encode_command(
            self,
            folderpath: str,
            filename: str,
            resolution: int,) -> List[str]:
        """
        nvencエンコード時のコマンド。動画のデコードにはSWが利用される。
        VBRでのエンコードを行う。
        エラー対策のため、実際に出力される動画の解像度は-1されている。
        """
        command = [
            "/opt/bin/ffmpeg",
            "-hide_banner",
            "-y",
            "-vsync 1",
            "-init_hw_device cuda",
            "-hwaccel_output_format cuda",
            f"-i {folderpath}/{filename}",
            "-c:v h264_nvenc",
            f"-b:v {self.bitrate[resolution]}M",
            f"-bufsize {self.bitrate[resolution]*2}M",
            "-b:a 192k",
            "-aac_coder twoloop",
            "-preset medium",
            "-profile:v high",
            "-bf 3",
            "-b_ref_mode 2",
            "-temporal-aq 1",
            f"-vf hwupload,scale_cuda=-2:{resolution-1}",
            "-hls_time 6",
            "-hls_list_size 0",
            "-f hls",
            f"{folderpath}/{resolution}p.m3u8",
        ]
        return command

    def thumbnail_command(
            self,
            folderpath: str,
            filename: str,
            resolution: int,
            s: int = 5) -> List[str]:
        """
        サムネイル生成のコマンド。
        引数sは切り出し時点の動画の場所。
        """
        command = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            f"-i {folderpath}/{filename}",
            f"-ss {s}",
            "-vframes 1",
            "-f image2",
            f"-vf scale=-2:{resolution}",
            f"{folderpath}/thumbnail_{resolution}.jpg"
        ]
        return command

    async def thumbnail(self, folderpath: str, filename: str):
        command = self.thumbnail_command(folderpath, filename, 360)
        await command_run(" ".join(command), "./")
        command = self.thumbnail_command(folderpath, filename, 720)
        await command_run(" ".join(command), "./")
        pass

    def video_info_command(self, folderpath: str, filename: str):
        command = [
            "ffprobe",
            "-loglevel quiet",
            "-show_streams",
            "-print_format json",
            f"{folderpath}/{filename}",
        ]
        return command

    async def get_video_info(
            self, folderpath: str, filename: str) -> dict:
        command = self.video_info_command(folderpath, filename)
        result = await command_run(" ".join(command), "./")
        try:
            result = json.loads(result.stdout)
        except ValueError:
            result = {}
        return result

    class video_resolution_class:
        def __init__(self, width: int, height: int, is_video: bool = True):
            self.is_video: bool = is_video
            self.width: int = width
            self.height: int = height

    async def get_video_resolution(
            self, folderpath: str, filename: str) -> video_resolution_class:
        result = await self.get_video_info(folderpath, filename)
        try:
            width = result["streams"][0]["width"]
            height = result["streams"][0]["height"]
            obj = self.video_resolution_class(width, height)
        except KeyError:
            obj = self.video_resolution_class(0, 0, False)
        return obj

    class encode_command_class:
        def __init__(self, encoder, command):
            self.encoder: str = encoder
            self.command: List[str] = command

    async def get_encode_command(
            self,
            folderpath: str,
            filename: str,
            resolution: int,) -> encode_command_class:
        if self.encode_worker == 0:
            await self.encode_test()

        # 利用可能なエンコーダーの探索
        use_encoder = None
        while True:
            for encoder in self.encoder_available:
                # 利用可能でかつ、利用されていない場合
                if self.encoder_available[encoder] and \
                        not self.encoder_used_status[encoder]:
                    # エンコーダーを利用状態にする
                    self.encoder_used_status[encoder] = True
                    use_encoder = encoder
                    break
            else:
                # 利用可能なエンコーダーがないときは待つ
                await asyncio.sleep(10)
                continue
            # breakされていたらもう一度break
            break

        # ソフトウエアエンコード
        if use_encoder == "software":
            command = self.software_encode_command(
                folderpath, filename, resolution)
        # vaapiエンコード
        elif use_encoder == "vaapi":
            command = self.vaapi_encode_command(
                folderpath, filename, resolution)
        # nvenc_hwエンコード
        elif use_encoder == "nvenc_hw_decode":
            command = self.nvenc_hw_decode_encode_command(
                folderpath, filename, resolution)
        # nvenc_swエンコード
        elif use_encoder == "nvenc_sw_decode":
            command = self.nvenc_sw_decode_encode_command(
                folderpath, filename, resolution)
        result = self.encode_command_class(use_encoder, command)
        return result

    async def encode(
            self,
            folderpath: str,
            filename: str,
            resolution: int,):
        logger.info("エンコード開始!!")
        encoder = await self.get_encode_command(folderpath, filename, resolution)
        logger.info("エンコーダ選択完了!!")
        # エンコード実行
        result = await command_run(" ".join(encoder.command), "./")
        # エンコーダーを開放
        self.encoder_used_status[encoder.encoder] = False
        if result.returncode == 0:
            return True
        else:
            logger.error("encoder error")
            logger.error(" ".join(encoder.command))
            # logger.error(result.stdout)
            # logger.error(result.stderr)
            return False

    async def encode_test(self):
        """
        エンコードのテスト
        """
        logger.info("エンコードテスト開始!!")
        self.encode_worker = 0
        # vaapi のテスト
        command = self.vaapi_encode_command(
            self.sample_dir, self.sample_video, 1080)
        result = await command_run(" ".join(command), "./")
        if result.returncode == 0:
            self.encoder_available["vaapi"] = True
            self.encode_worker += 1

        # nvenc(HW) のテスト
        command = self.nvenc_hw_decode_encode_command(
            self.sample_dir, self.sample_video, 1080)
        result = await command_run(" ".join(command), "./")
        if result.returncode == 0:
            self.encoder_available["nvenc_hw_decode"] = True
            self.encode_worker += 1

        # nvenc(SW) のテスト
        command = self.nvenc_sw_decode_encode_command(
            self.sample_dir, self.sample_video, 1080)
        result = await command_run(" ".join(command), "./")
        if result.returncode == 0:
            self.encoder_available["nvenc_sw_decode"] = True
            self.encode_worker += 1

        # ソフトウエアエンコードしか使えない場合
        if self.encode_worker == 0:
            self.encoder_available["software"] = True
            self.encode_worker = 1

        logger.info("エンコードテスト完了!!")
        return self.encoder_available


encoder = encoder_class()
