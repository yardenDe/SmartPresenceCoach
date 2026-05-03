import cv2
from typing import Generator, List
import numpy as np


class VideoExtractor:
    def __init__(self, video_path: str):
        self.video_path = video_path

    def get_chunks(self, chunk_sec: int = 3, target_fps: int = 3) -> Generator[List[np.ndarray], None, None]:

        frames_needed_per_chunk = chunk_sec * target_fps
        current_chunk = []

        for frame in self.get_frames(target_fps=target_fps):
            current_chunk.append(frame)

            if len(current_chunk) >= frames_needed_per_chunk:
                yield current_chunk 
                current_chunk = []

        if current_chunk:
            yield current_chunk


    def get_frames(
    self,
    target_fps: int = 3,
    target_size: tuple[int, int] = (640, 480)
) -> Generator[np.ndarray, None, None]:
        
        cap = cv2.VideoCapture(self.video_path)
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if video_fps <= 0: video_fps = 30 
        step = max(1, int(video_fps / target_fps))

        frame_index = 0
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break

                if frame_index % step == 0:
                    if target_size and (frame.shape[1], frame.shape[0]) != target_size:
                        frame = cv2.resize(frame, target_size)
                    yield frame

                frame_index += 1
        finally:
            cap.release()




