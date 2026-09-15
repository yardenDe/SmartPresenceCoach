from dataclasses import fields
from typing import Any

from mediapipe.tasks.python.vision import PoseLandmark, PoseLandmarkerResult

from core.logger import get_logger
from vision.config import FrameLandmarks, Landmark
from vision.mediapipe_detector import MediaPipeDetector


logger = get_logger("app.vision.pipeline")


class VisionPipeline:
    def __init__(
        self,
        detector: MediaPipeDetector,
    ):
        self.detector = detector
        logger.debug("event=vision.pipeline.init")

    def _extract_landmarks(
        self,
        pose_result: PoseLandmarkerResult,
    ) -> FrameLandmarks | None:
        if not pose_result.pose_landmarks:
            return None

        pose_landmarks = pose_result.pose_landmarks[0]
        extracted = {}

        for field in fields(FrameLandmarks):
            pose_landmark = PoseLandmark[field.name.upper()]
            point = pose_landmarks[pose_landmark.value]

            extracted[field.name] = Landmark(
                x=point.x,
                y=point.y,
            )

        return FrameLandmarks(**extracted)

    def process(
        self,
        frames: Any,
    ) -> list[FrameLandmarks]:
        results = []

        for frame in frames:
            pose_result = self.detector.detect(frame)
            landmarks = self._extract_landmarks(pose_result)

            if landmarks is not None:
                results.append(landmarks)

        logger.debug(
            "event=vision.chunk.done frames=%s landmarks=%s empty_frames=%s",
            len(frames),
            len(results),
            len(frames) - len(results),
        )

        return results