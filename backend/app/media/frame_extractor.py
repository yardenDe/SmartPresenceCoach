import cv2
import numpy as np
from collections.abc import Generator

from core.exceptions import InvalidVideoError
from core.logger import get_logger
from media.config import TARGET_FPS, MS_IN_SEC

logger = get_logger("app.media.frame_extractor")


class FrameExtractor:
    def __init__(
        self,
        target_fps: int = TARGET_FPS,
    ):
        self.target_fps = target_fps

    def get_chunks(
        self,
        video_path: str,
        chunk_sec: float,
    ) -> Generator[list[np.ndarray], None, None]:

        chunk_size = chunk_sec * self.target_fps
        chunk = []

        for frame in self._get_frames(video_path):
            chunk.append(frame)

            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        
        if chunk:
            yield chunk

    def extract(
        self,
        video_path: str,
    ) -> list[np.ndarray]:
        return list(self._get_frames(video_path))
        
    def _get_frames(
        self,
        video_path: str,
    ) -> Generator[np.ndarray, None, None]:

        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error("event=video.open.failed")
            raise InvalidVideoError()


        sample_interval = 1 / self.target_fps
        next_sample_time = 0.0

        try:
            while True:
                success, frame = cap.read()

                if not success:
                    break

                current_time = (
                    cap.get(cv2.CAP_PROP_POS_MSEC)
                    / MS_IN_SEC
                )

                if current_time >= next_sample_time:
                    yield frame
                    next_sample_time += sample_interval


        except Exception as e:
            logger.exception(
                "event=video.extract.failed error=%s",
                str(e),
            )
            raise InvalidVideoError() from e

        finally:
            cap.release()