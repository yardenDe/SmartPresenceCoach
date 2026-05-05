import cv2
from typing import Generator, List
import numpy as np

from core.exceptions import InvalidVideoError
from core.logger import get_logger

logger = get_logger("app.vision.video_extractor")


class VideoExtractor:
    def __init__(self, video_path: str):
        self.video_path = video_path

    def get_chunks(
        self,
        chunk_sec: int = 3,
        target_fps: int = 3
    ) -> Generator[List[np.ndarray], None, None]:

        frames_needed_per_chunk = chunk_sec * target_fps
        current_chunk: List[np.ndarray] = []
        chunk_index = 0

        for frame in self.get_frames(target_fps=target_fps):
            current_chunk.append(frame)

            if len(current_chunk) >= frames_needed_per_chunk:
                chunk_index += 1
                logger.debug(
                    "event=video.chunk.ready chunk=%s frames=%s",
                    chunk_index,
                    len(current_chunk)
                )
                yield current_chunk
                current_chunk = []

        if current_chunk:
            chunk_index += 1
            logger.debug(
                "event=video.chunk.ready chunk=%s frames=%s",
                chunk_index,
                len(current_chunk)
            )
            yield current_chunk

        logger.debug("event=video.chunks.done total_chunks=%s", chunk_index)

    def get_frames(
        self,
        target_fps: int = 3,
        target_size: tuple[int, int] = (640, 480)
    ) -> Generator[np.ndarray, None, None]:

        cap = cv2.VideoCapture(self.video_path)
        frame_index = 0
        sampled_frames = 0

        try:
            if not cap.isOpened():
                logger.error("event=video.open.failed")
                raise InvalidVideoError()

            video_fps = cap.get(cv2.CAP_PROP_FPS)
            if video_fps <= 0:
                video_fps = 30

            step = max(1, int(video_fps / target_fps))

            logger.debug(
                "event=video.open.done fps=%.2f target_fps=%s step=%s",
                video_fps,
                target_fps,
                step
            )

            while True:
                success, frame = cap.read()

                if not success:
                    logger.debug(
                        "event=video.read.end frame_index=%s sampled=%s",
                        frame_index,
                        sampled_frames
                    )
                    break

                if frame_index % step == 0:

                    if target_size and (
                        frame.shape[1], frame.shape[0]
                    ) != target_size:
                        frame = cv2.resize(frame, target_size)

                    sampled_frames += 1
                    yield frame

                frame_index += 1

        except InvalidVideoError:
            raise
        except Exception as e:
            logger.exception(
                "event=video.extract.failed error=%s",
                str(e)
            )
            raise InvalidVideoError()

        finally:
            cap.release()
            logger.debug(
                "event=video.read.done frames=%s sampled=%s",
                frame_index,
                sampled_frames
            )
