from typing import Any

from core.logger import get_logger
from vision.mediapipe_detector import MediaPipeDetector
from vision.landmark_extractor import LandmarkExtractor


logger = get_logger("app.vision.pipeline")


class VisionPipeline:
    def __init__(
        self,
        detector: MediaPipeDetector,
        landmark_extractor: LandmarkExtractor,
    ):
        self.detector = detector
        self.landmark_extractor = landmark_extractor
        logger.debug("event=vision.pipeline.init")

    def process_frame(self, frame: Any) -> dict[str, Any]:
        pose_result = self.detector.detect(frame)
        landmarks = self.landmark_extractor.filter_landmarks(pose_result)
        if not landmarks:
            logger.debug("event=vision.frame.no_landmarks")
            return {}

        logger.debug("event=vision.frame.done has_pose=true")
        return landmarks

    def process(self, frames: Any) -> list[dict[str, Any]]:
        chunk_results = []

        for frame in frames:
            landmarks = self.process_frame(frame)
            if landmarks:
                chunk_results.append(landmarks)
                
        logger.debug(
            "event=vision.chunk.done frames=%s landmarks=%s empty_frames=%s",
            len(frames),
            len(chunk_results),
            len(chunk_results)-len(frames),
        )
        return chunk_results
