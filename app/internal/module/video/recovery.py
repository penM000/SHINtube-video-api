import pathlib
from .database import database
from .queue import add_encode_queue
from ..logger import logger
video_dir = "video"


class recovery_class():
    def audio_recovery(self):
        video_path = pathlib.Path("./")
        audio_files_path = video_path.glob("**/audio.m3u8")
        for i in audio_files_path:
            done_file_path = i.parent / "audio.done"
            if not done_file_path.exists():
                i.unlink()

    async def file_recovery(self):
        folder_paths = pathlib.Path("./").glob("**/info.json")
        for folder_path in folder_paths:
            done_file_path = folder_path.parent / "file.done"
            if not done_file_path.exists():
                logger.warning(f"file write error {folder_path.parent}")
                await database.encode_error(str(folder_path.parent), "file write error")

    async def runrecovery(self):
        await self.file_recovery()
        self.audio_recovery()
        tasks = await database.get_encode_tasks()
        for task in tasks:
            for encode_resolution in task["encode_tasks"]:
                await add_encode_queue(folderpath=task["video_directory"],
                                       filename=task["video_file_name"],
                                       encode_resolution=int(encode_resolution[:-1]))
        pass


recovery = recovery_class()
