from .filemanager import filemanager
from ..command_run import command_run
from ..logger import logger
import json
import asyncio
from typing import List
from dataclasses import dataclass
import pathlib


class encoder_class:
    def __init__(self):
        # サンプル動画
        self.sample_dir = "./sample"
        self.sample_video = "video.mp4"
        # 解像度:ビットレート(Mbps)
        self.bitrate = {
            1080: 4.3,
            720: 2.3,
            480: 1.2,
            360: 0.65,
            240: 0.24,
            160: 0.24
        }
        # 利用可能なエンコーダ
        self.encoder_available = {
            "vaapi": False,
            "nvenc_sw_decode1": False,
            "nvenc_sw_decode2": False,
            "software": False
        }
        # 同時エンコード数
        self.encode_worker = 0
        # 現在利用中のエンコーダ
        self.encoder_used_status = {
            "vaapi": False,
            "nvenc_sw_decode1": False,
            "nvenc_sw_decode2": False,
            "software": False
        }

    def audio_encode_command(
            self,
            folderpath: str,
            filename: str,
            bitrate: int = 192):
        """
        オーディオ切り出しのコマンド
        """

        command = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-analyzeduration 30M",
            "-probesize 30M",
            f"-i {folderpath}/{filename}",
            "-vn",
            f"-b:a {bitrate}k",
            "-aac_coder twoloop",
            "-start_number 0",
            "-hls_time 6",
            "-hls_list_size 0",
            "-f hls",
            f"{folderpath}/audio.m3u8"
        ]
        return command

    def software_encode_command(
            self,
            folderpath: str,
            filename: str,
            resolution: int,
            bitrate: float = 4,
            thread: int = 0) -> List[str]:
        """
        ソフトウエアエンコード時のコマンド。
        遅い。
        """
        command = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-analyzeduration 30M",
            "-probesize 30M",
            "-vsync 1",
            f"-threads {thread}",
            f"-i {folderpath}/{filename}",
            "-g 180",
            f"-threads {thread}",
            "-vcodec libx264",
            "-bf 8",
            f"-b:v {bitrate}M",
            f"-bufsize {round(bitrate*6,2)}M",
            "-bsf:v 'filter_units=pass_types=1-5'",
            "-an",
            "-start_number 0",
            "-hls_time 6",
            "-hls_list_size 0",
            "-f hls",
            (
                "-vf framerate=30,"
                f"scale=-2:{resolution}:flags=lanczos+accurate_rnd"
            ),
            f"{folderpath}/{resolution}p.m3u8"
        ]
        return command

    def vaapi_sw_encode_command(
            self,
            folderpath: str,
            filename: str,
            resolution: int,
            bitrate: float = 4,
            vaapi_device: str = "/dev/dri/renderD128") -> List[str]:
        """
        vaapi(intel)エンコード時のコマンド。
        VBRでのエンコードを行う。
        """
        command = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-analyzeduration 30M",
            "-probesize 30M",
            "-vsync 1",
            f"-init_hw_device vaapi=intel:{vaapi_device}",
            "-filter_hw_device intel",
            f"-i {folderpath}/{filename}",
            "-g 180",
            "-vcodec h264_vaapi",
            "-rc_mode VBR",
            "-bf 8",
            f"-b:v {bitrate}M",
            f"-bufsize {round(bitrate*6,2)}M",
            "-bsf:v 'filter_units=pass_types=1-5'",
            "-an",
            (
                "-vf 'framerate=30,format=nv12,hwupload,"
                f"scale_vaapi=w=-2:h={resolution}'"
            ),
            "-profile high",
            "-compression_level 0",
            "-start_number 0",
            "-hls_time 6",
            "-hls_list_size 0",
            "-f hls",
            f"{folderpath}/{resolution}p.m3u8"]
        return command

    def nvenc_sw_decode_encode_command(
            self,
            folderpath: str,
            filename: str,
            resolution: int,
            bitrate: float = 4) -> List[str]:
        """
        nvencエンコード時のコマンド。動画のデコードにはSWが利用される。
        VBRでのエンコードを行う。
        エラー対策のため、実際に出力される動画の解像度は-1されている。
        """
        command = [
            "/opt/bin/ffmpeg",
            "-hide_banner",
            "-y",
            "-analyzeduration 30M",
            "-probesize 30M",
            "-vsync 1",
            "-init_hw_device cuda",
            "-hwaccel_output_format cuda",
            f"-i {folderpath}/{filename}",
            "-g 180",
            "-c:v h264_nvenc",
            f"-b:v {bitrate}M",
            f"-bufsize {round(bitrate*6,2)}M",
            "-an",
            "-preset medium",
            "-profile:v high",
            "-bf 4",
            "-b_ref_mode 2",
            "-bsf:v 'filter_units=pass_types=1-5'",
            "-temporal-aq 1",
            (
                "-vf framerate=30,format=nv12,hwupload,"
                f"scale_cuda=-2:{resolution-1}:interp_algo=lanczos"
            ),
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
            f"-vf scale=-2:{resolution}:flags=lanczos+accurate_rnd",
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

    @dataclass
    class video_info_class:
        """Class for keeping track of an item in inventory."""
        is_video: bool = False
        is_audio: bool = False
        video_bitrate: int = 0
        audio_bitrate: int = 0
        width: int = 0
        height: int = 0

    async def get_video_info(
            self, folderpath: str, filename: str) -> video_info_class:
        # ffprobe で解析
        command = self.video_info_command(folderpath, filename)
        result = await command_run(" ".join(command), "./")
        try:
            result = json.loads(result.stdout)
        except ValueError:
            result = {}
        obj = self.video_info_class()
        # ビデオストリームがない場合
        if "streams" not in result:
            return obj

        for stream in result["streams"]:
            if "codec_type" in stream:
                if "audio" == stream["codec_type"]:
                    obj.is_audio = True
                    if "bit_rate" in stream:
                        obj.audio_bitrate = int(stream["bit_rate"])
                    else:
                        # 30Mbitぐらい
                        obj.audio_bitrate = 30 * (1024**2)
                elif "video" == stream["codec_type"]:
                    obj.is_video = True
                    obj.width = int(stream["width"])
                    obj.height = int(stream["height"])
                    if "avg_frame_rate" in stream:
                        if stream["avg_frame_rate"] == "0/0":
                            obj.is_video = False
                    if "duration" in stream:
                        # 入力ファイルからビットレートを推定
                        video_file_path = pathlib.Path(folderpath) / filename
                        video_file_size = video_file_path.stat().st_size
                        video_bitrate = video_file_size * \
                            8 / float(stream["duration"])
                        video_bitrate = int(video_bitrate)
                        # logger.info(f"入力ビットレート:{video_bitrate}")
                        # コーデックごとのビットレート倍率
                        if "codec_name" in stream:
                            if stream["codec_name"] == "av1":
                                obj.video_bitrate = video_bitrate * 2.5
                            elif stream["codec_name"] == "vp9":
                                obj.video_bitrate = video_bitrate * 1.7
                            elif stream["codec_name"] == "hevc":
                                obj.video_bitrate = video_bitrate * 1.7
                            else:
                                obj.video_bitrate = video_bitrate * 1.1
                        else:
                            # 30Mbitぐらい
                            obj.video_bitrate = 30 * (1024**2)
                    else:
                        # 30Mbitぐらい
                        obj.video_bitrate = 30 * (1024**2)
        return obj

    @dataclass
    class encode_command_class:
        encoder: str = ""
        command: list = ""
        bitrate: float = 0.0

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
                await asyncio.sleep(1)
                continue
            # breakされていたらもう一度break
            break
        # 動画ビットレートを算出
        video_info = await self.get_video_info(folderpath, filename)
        # 単位をMbpsに修正
        input_video_bitrate = (
            float(video_info.video_bitrate) / (1024**2))
        bitrate = float(min(self.bitrate[resolution], input_video_bitrate))

        # ソフトウエアエンコード
        if use_encoder == "software":
            command = self.software_encode_command(
                folderpath, filename, resolution, bitrate)
        # vaapiエンコード
        elif use_encoder == "vaapi":
            command = self.vaapi_sw_encode_command(
                folderpath, filename, resolution, bitrate)
        # nvenc_swエンコード1
        elif use_encoder == "nvenc_sw_decode1":
            command = self.nvenc_sw_decode_encode_command(
                folderpath, filename, resolution, bitrate)
        # nvenc_swエンコード2
        elif use_encoder == "nvenc_sw_decode2":
            command = self.nvenc_sw_decode_encode_command(
                folderpath, filename, resolution, bitrate)
        result = self.encode_command_class()
        result.encoder = use_encoder
        result.command = command
        result.bitrate = bitrate
        return result

    async def encode_audio(
            self,
            folderpath: str,
            filename: str,
            force: bool = False):
        encode_path = pathlib.Path(folderpath)
        # 入力ファイルの状態を取得
        video_info = await self.get_video_info(folderpath, filename)
        # 音声ストリームがない場合
        if not video_info.is_audio:
            # 空のaudio.doneを作成
            (encode_path / "audio.done").touch()
            return True
        # audio.m3u8がファイルが存在していた場合
        if (encode_path / "audio.m3u8").exists() or force:
            return True

        # 空のaudio.m3u8を作成
        (encode_path / "audio.m3u8").touch()

        # ビットレート算出 単位をkbpsに修正
        input_audio_bitrate = int(video_info.audio_bitrate) / 1024
        # 上限192Kbps 下限128Kbps
        bitrate = int(min(192, max(input_audio_bitrate, 128)))

        # audioのエンコード
        logger.info(f"音声エンコード開始 {folderpath}")
        command = self.audio_encode_command(
            folderpath, filename, bitrate)

        # エンコード実行
        await command_run(" ".join(command), "./")

        # プレイリストに書き込み
        playlist_path = f"{folderpath}/playlist.m3u8"
        await filemanager.write_playlist(playlist_path, "audio")
        logger.info(f"音声エンコード終了 {folderpath}")

        # 空のaudio.doneを作成
        (encode_path / "audio.done").touch()

        return True

    async def encode(
            self,
            folderpath: str,
            filename: str,
            resolution: int,):

        logger.info(f"エンコード開始 {folderpath} {resolution}")
        # 音声エンコード(別タスクで実行)
        asyncio.create_task(self.encode_audio(folderpath, filename))

        encoder = await self.get_encode_command(
            folderpath, filename, resolution)
        logger.info(f"動画エンコード開始 エンコーダ{encoder.encoder}を利用")
        # エンコード実行
        result = await command_run(" ".join(encoder.command), "./")
        logger.info(f"動画エンコード終了 エンコーダ{encoder.encoder}を開放")
        logger.info(f"エンコード終了 {folderpath} {resolution}")
        # エンコーダーを開放
        self.encoder_used_status[encoder.encoder] = False

        if result.returncode == 0:
            return True
        else:
            logger.error(f"encoder error {folderpath}")
            logger.error(" ".join(encoder.command))
            logger.error(result.stdout)
            logger.error(result.stderr)
            return False

    async def encode_test(self):
        """
        エンコードのテスト
        """
        logger.info("エンコードテスト開始")
        self.encode_worker = 0

        # vaapi のテスト
        command = self.vaapi_sw_encode_command(
            self.sample_dir, self.sample_video, 1080)
        result = await command_run(" ".join(command), "./")
        if result.returncode == 0:
            self.encoder_available["vaapi"] = True
            self.encode_worker += 1
        else:
            logger.warning("encoder test failed vaapi")
            logger.warning(" ".join(command))
            logger.warning(result.stdout)
            logger.warning(result.stderr)
        # nvenc(SW) のテスト
        command = self.nvenc_sw_decode_encode_command(
            self.sample_dir, self.sample_video, 1080)
        result = await command_run(" ".join(command), "./")
        if result.returncode == 0:
            self.encoder_available["nvenc_sw_decode1"] = True
            self.encoder_available["nvenc_sw_decode2"] = True
            self.encode_worker += 2
            # nvencが利用可能ならばvaapiを使わないほうが早い
            if self.encoder_available["vaapi"]:
                self.encoder_available["vaapi"] = False
                self.encode_worker -= 1
        else:
            logger.warning("encoder test failed nvenc")
            logger.warning(" ".join(command))
            logger.warning(result.stdout)
            logger.warning(result.stderr)

        # ソフトウエアエンコードしか使えない場合
        if self.encode_worker == 0:
            self.encoder_available["software"] = True
            self.encode_worker = 1

        logger.info("エンコードテスト完了")
        logger.info(f"{self.encoder_available}")
        logger.info(f"エンコードworker数={self.encode_worker}")
        return self.encoder_available


encoder = encoder_class()
