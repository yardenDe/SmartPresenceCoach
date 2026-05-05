import os
import tempfile
from fastapi import UploadFile

from core.logger import get_logger

logger = get_logger("app.vision.video_storage")

class VideoStorage:

    async def save_temp(self, video: UploadFile) -> str:
        try:
            if not video:
                raise ValueError("No video provided")

            suffix = os.path.splitext(video.filename or "")[1] or ".mp4"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                while True:
                    chunk = await video.read(1024 * 1024)
                    if not chunk:
                        break
                    temp_file.write(chunk)
                temp_file.flush()

                if not os.path.exists(temp_file.name):
                    raise RuntimeError("Temp file was not created")

                return temp_file.name
            
        except Exception:
            logger.exception("event=video.save.failed")
            raise

    def delete(self, path: str) -> None:
        if path and os.path.exists(path):
            os.remove(path)
