import asyncio
from dataclasses import dataclass


class CommandClass:
    def __init__(self):
        pass

    @dataclass
    class CommandResultClass:
        """コマンド実行時の返り値の構造"""
        returncode: int
        stdout: str
        stderr: str

    def _list_to_str_command(self, command):
        return " ".join(command)

    async def command_run(self,
                          cmd,
                          cwd,
                          normal_mode=True) -> CommandResultClass:
        if isinstance(cmd, list):
            cmd = self._list_to_str_command(cmd)
        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        if normal_mode:
            stdout, stderr = await proc.communicate()
            if stdout:
                pass
                # print(f'[stdout]\n{stdout.decode()}')
            if stderr:
                pass
                # print(f'[stderr]\n{stderr.decode()}')
            result = self.CommandResultClass(
                proc.returncode,
                f'{stdout.decode()}',
                f'{stderr.decode()}')
        else:
            while proc.returncode is None:
                line = await proc.stderr.readline()
                line = line
                # print(line.decode().replace("\n", ""))
        return result
