from typing import Any

from core.logger import get_logger
from vision.mediapipe_detector import MediaPipeDetector
from vision.landmark_extractor import LandmarkExtractor


logger = get_logger("app.vision.pipeline")


class VisionPipeline:
    def __init__(self, detector: MediaPipeDetector):
        self.detector = detector
        self.landmark_extractor = LandmarkExtractor()
        logger.debug("event=vision.pipeline.init")

    def process_frame(self, frame: Any) -> dict[str, Any]:
        raw = self.detector.detect(frame)
        if not raw:
            logger.debug("event=vision.frame.empty_detection")
            return {}

        landmarks = self.landmark_extractor.filter_landmarks(raw)
        if not landmarks:
            logger.debug("event=vision.frame.no_landmarks")
            return {}

        logger.debug("event=vision.frame.done has_pose=true")
        return landmarks

    def process(self, frames: Any) -> list[dict[str, Any]]:
        chunk_results = []
        empty_frames = 0

        for frame in frames:
            landmarks = self.process_frame(frame)
            if landmarks:
                chunk_results.append(landmarks)
            else:
                empty_frames += 1

        logger.debug(
            "event=vision.chunk.done frames=%s landmarks=%s empty_frames=%s",
            len(frames),
            len(chunk_results),
            empty_frames,
        )
        return chunk_results
