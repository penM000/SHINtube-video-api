import asyncio


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
    else:
        while proc.returncode is None:
            line = await proc.stderr.readline()
            print(line.decode().replace("\n", ""))
    return proc.returncode
