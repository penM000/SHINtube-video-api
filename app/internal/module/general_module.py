import asyncio
import json
# import pathlib
import random
import string
from functools import wraps, partial

import aiofiles
from fastapi import File, UploadFile

from .submodule.command import CommandClass


class GeneralModuleClass(CommandClass):
    def __init__(self):
        pass

    def async_wrap(self, func):
        """
        同期処理を非同期化する関数
        https://stackoverflow.com/a/50450553
        """
        @wraps(func)
        async def run(*args, loop=None, executor=None, **kwargs):
            if loop is None:
                loop = asyncio.get_event_loop()
            pfunc = partial(func, *args, **kwargs)
            return await loop.run_in_executor(executor, pfunc)
        return run

    def GetRandomStr(self, num) -> str:
        """
        ランダムな文字列を生成する関数
        https://pg-chain.com/python-random-2
        """
        # 英数字をすべて取得
        dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
        # 英数字からランダムに取得
        return ''.join([random.choice(dat) for i in range(num)])

    async def read_file(self, file_path) -> str:
        """
        非同期でファイルを読み込む関数
        """
        file_path = str(file_path)
        file_data = None

        async with aiofiles.open(file_path, "r") as f:
            file_data = await f.read()

        return file_data

    async def read_json(self, file_path) -> dict:
        """
        非同期でjsonを読み込む関数
        """
        try:
            json_data = await self.read_file(file_path)
            python_dict = json.loads(json_data)
        except Exception:
            return {}
        else:
            return python_dict

    async def write_file(self, file_path, in_file: UploadFile = File(...)):
        """
        非同期でUploadFileをファイルに書き込む関数
        """
        in_file.file.seek(0)
        async with aiofiles.open(file_path, 'wb') as out_file:
            while True:
                # 書き込みサイズ(MB)
                chunk = 32
                # async read chunk
                content = await in_file.read(chunk * 1048576)
                if content:
                    await out_file.write(content)  # async write chunk
                else:
                    break

    def write_json(self, file_path, python_dict) -> bool:
        """
        同期でjsonを書き込む関数
        """
        try:
            with open(file_path, "w") as f:
                json.dump(python_dict, f, indent=4)
        except Exception:
            return False
        else:
            return True


general_module = GeneralModuleClass()
