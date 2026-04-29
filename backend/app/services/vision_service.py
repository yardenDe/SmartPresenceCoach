from typing import Any, Iterator, List, Dict, Optional

from core.logger import get_logger
from vision.video_extractor import VideoExtractor
from vision.frame_extractor import FrameExtractor
from vision.mp_detector import MediaPipeDetector
from vision.landmark_extractor import LandmarkManager


class VisionPipeline:

    def __init__(self, video_path: Optional[str] = None, mode: int = 1):
        self.video_path = video_path
        self.mode = mode

        self.logger = get_logger("app.vision.pipeline")
        
        self.frame_extractor = FrameExtractor(video_path) if video_path else None
        self.video_extractor = VideoExtractor(video_path) if video_path else None
        self.detector = MediaPipeDetector()
        self.landmark_manager = LandmarkManager()


    def _get_detector_modes(self) -> dict[str, bool]:
        return {
            "pose_mode": True,
            "face_mode": self.mode >= 2,
            "hand_mode": self.mode >= 2,
        }

    def process_frame(self, frame: Any) -> Dict[str, Any]:

        raw = self.detector.detect(
            frame,
            **self._get_detector_modes()
        )

        if not raw:
            return {}

        return self.landmark_manager.filter_landmarks(raw)

   
    def process_chunk(self):

        chunk_results = []

        for frame in self.frame_extractor.get_frames():
            landmarks = self.process_frame(frame)

            if landmarks:
                chunk_results.append(landmarks)

        return chunk_results
    
    def process_video(self):

        for chunk in self.video_extractor.get_chunks():
            yield self.process_chunk(chunk)
    

    def pipline(self, mode: str = "offline"):

        if mode == "offline":
            yield self.process_video()
        elif mode == "online":
            return self.process_chunk()
        else:
            raise ValueError(f"Unknown mode: {mode}")

   
    def close(self):
        self.detector.close()