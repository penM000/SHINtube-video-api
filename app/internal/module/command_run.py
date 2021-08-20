import asyncio
from dataclasses import dataclass


@dataclass
class command_result:
    """Class for keeping track of an item in inventory."""
    returncode: int
    stdout: str
    stderr: str


async def command_run(cmd, cwd, normal_mode=True):
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
        result = command_result(
            proc.returncode,
            f'{stdout.decode()}',
            f'{stderr.decode()}')
    else:
        while proc.returncode is None:
            line = await proc.stderr.readline()
            #print(line.decode().replace("\n", ""))

    return result
