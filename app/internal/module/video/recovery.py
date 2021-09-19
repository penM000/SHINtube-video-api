import pathlib
from .database import database
from .queue import add_encode_queue
video_dir = "video"


class recovery_class():
    def audio_recovery(self):
        video_path = pathlib.Path("./")
        audio_files_path = video_path.glob("**/audio.m3u8")
        for i in audio_files_path:
            done_file_path = i.parent / "audio.done"
            if not done_file_path.exists():
                i.unlink()

    async def runrecovery(self):
        self.audio_recovery()
        tasks = await database.get_encode_tasks()
        for task in tasks:
            for encode_resolution in task["encode_tasks"]:
                await add_encode_queue(folderpath=task["video_directory"],
                                       filename=task["video_file_name"],
                                       encode_resolution=int(encode_resolution[:-1]))
        pass


recovery = recovery_class()
