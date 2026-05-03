from typing import Any, Dict, Generator, Optional

from core.logger import get_logger
from vision.video_extractor import VideoExtractor
from vision.mediapipe_detector import MediaPipeDetector
from vision.landmark_extractor import LandmarkExtractor

class VisionPipeline:

    def __init__(self, detector: MediaPipeDetector, level: int = 1):
        self.mode = level

        self.logger = get_logger("app.vision.pipeline")
        
        self.video_extractor = None
        self.detector = detector
        self.landmark_extractor = LandmarkExtractor()


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

        return self.landmark_extractor.filter_landmarks(raw)
   
    def process_chunk(self, frames: Any) -> list[dict[str, Any]]:

        chunk_results = []
        
        for frame in frames:
            landmarks = self.process_frame(frame)

            if landmarks:
                chunk_results.append(landmarks)

        return chunk_results
    
  

    def pipline(
        self,
        video_path: str,
    ) -> Generator[list[dict[str, Any]], None, list[dict[str, Any]] | None]:

        self.video_extractor = VideoExtractor(video_path=video_path)
        for chunk_frames in self.video_extractor.get_chunks(chunk_sec=3, target_fps=3):
            yield self.process_chunk(chunk_frames)

    def close(self) -> None:
        self.detector.close()
