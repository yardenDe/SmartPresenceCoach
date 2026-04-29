import cv2
from typing import Generator, List

class VideoExtractor:
    def __init__(self, video_path):
        self.video_path = video_path

    def get_chunks(self, chunk_sec=3) -> Generator[List, None, None]:
        cap = cv2.VideoCapture(self.video_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
            fps = 30

        chunk_frames = int(fps*chunk_sec)

        chunk = []
        frame_count = 0

        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break

                chunk.append(frame)
                frame_count += 1

                if frame_count >= chunk_frames:
                    yield chunk
                    chunk = []
                    frame_count = 0

            if chunk:
                yield chunk

        finally:
            cap.release()