import cv2
import numpy as np
from collections.abc import Generator

from core.exceptions import InvalidVideoError
from core.logger import get_logger
from video.config import CHUNK_SECONDS, TARGET_FPS

logger = get_logger("app.video.frame_extractor")


class FrameExtractor:
    def __init__(
        self,
        video_path: str,
        target_fps: int = TARGET_FPS,
    ):
        self.video_path = video_path
        self.target_fps = target_fps

    def get_chunks(
        self,
        chunk_sec: int = CHUNK_SECONDS,
    ) -> Generator[list[np.ndarray], None, None]:

        chunk_size = chunk_sec * self.target_fps
        chunk = []

        for frame in self._get_frames():
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
    ) -> Generator[np.ndarray, None, None]:

        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            logger.error("event=video.open.failed")
            raise InvalidVideoError()

        video_fps = cap.get(cv2.CAP_PROP_FPS)

        if video_fps <= 0:
            cap.release()
            raise InvalidVideoError()

        frame_index = 0
        sample_interval = 1 / self.target_fps
        next_sample_time = 0.0

        try:
            while True:
                success, frame = cap.read()

                if not success:
                    break

                current_time = frame_index / video_fps

                if current_time >= next_sample_time:
                    yield frame
                    next_sample_time += sample_interval

                frame_index += 1

        except Exception as e:
            logger.exception(
                "event=video.extract.failed error=%s",
                str(e),
            )
            raise InvalidVideoError() from e

        finally:
            cap.release()