import os
import tempfile
from datetime import datetime
from fastapi import UploadFile

from core.exceptions import VideoSaveError
from core.logger import get_logger

logger = get_logger("app.vision.storage")

class storage:

    async def save_temp(self, video: UploadFile) -> str:
        try:
            if not video:
                raise VideoSaveError()

            prefix = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            suffix = os.path.splitext(video.filename or "")[1] or ".mp4"
            with tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix=suffix) as temp_file:
                size_bytes = 0
                while True:
                    chunk = await video.read(1024 * 1024)
                    if not chunk:
                        break
                    size_bytes += len(chunk)
                    temp_file.write(chunk)
                temp_file.flush()

                if not os.path.exists(temp_file.name):
                    raise VideoSaveError()

                if size_bytes == 0:
                    raise VideoSaveError()

                logger.info("event=video.save.done size=%s suffix=%s", size_bytes, suffix)
                return temp_file.name
            
        except VideoSaveError:
            logger.warning("event=video.save.invalid")
            raise
        except Exception:
            logger.exception("event=video.save.failed")
            raise VideoSaveError()

    def delete(self, path: str) -> None:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                logger.debug("event=video.delete.done")
        except Exception:
            logger.exception("event=video.delete.failed")
