import os
import tempfile
from fastapi import UploadFile


class VideoStorage:

    async def save_temp(self, video: UploadFile) -> str:

        suffix = os.path.splitext(video.filename or "")[1] or ".mp4"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:

            while True:
                chunk = await video.read(1024 * 1024)
                if not chunk:
                    break
                temp_file.write(chunk)

            temp_file.flush()

            return temp_file.name

    def delete(self, path: str) -> None:
        if path and os.path.exists(path):
            os.remove(path)
