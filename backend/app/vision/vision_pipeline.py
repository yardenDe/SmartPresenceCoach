from typing import Any, Dict

from core.logger import get_logger
from vision.mediapipe_detector import MediaPipeDetector
from vision.landmark_extractor import LandmarkExtractor


logger = get_logger("app.vision.pipeline")


class VisionPipeline:

    def __init__(self, detector: MediaPipeDetector, level: int = 1):
        self.mode = level
        self.detector = detector
        self.landmark_extractor = LandmarkExtractor()

        logger.debug("event=vision.pipeline.init mode=%s", self.mode)


    def _get_detector_modes(self) -> dict[str, bool]:
        return {
            "pose_mode": True,
            "face_mode": self.mode >= 2,
            "hand_mode": self.mode >= 2,
        }


    def _has_landmarks(self, landmarks: dict[str, Any]) -> bool:
        return bool(
            landmarks.get("pose")
            or landmarks.get("face")
            or landmarks.get("hands")
        )


    def process_frame(self, frame: Any) -> Dict[str, Any]:
        raw = self.detector.detect(
            frame,
            **self._get_detector_modes()
        )

        if raw:
            logger.debug(
                "event=vision.detect.done has_pose=%s has_face=%s has_hands=%s",
                raw.get("pose_landmarks") is not None,
                raw.get("face_landmarks") is not None,
                raw.get("hands_landmarks") is not None,
            )
        else:
            logger.debug("event=vision.frame.empty_detection")
            return {}

        landmarks = self.landmark_extractor.filter_landmarks(raw)

        if not self._has_landmarks(landmarks):
            logger.debug("event=vision.frame.no_landmarks")
            return {}

        logger.debug(
            "event=vision.frame.done has_pose=%s has_face=%s hands=%s",
            landmarks.get("pose") is not None,
            landmarks.get("face") is not None,
            len(landmarks.get("hands") or []),
        )

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


    def close(self) -> None:
        logger.debug("event=vision.pipeline.close")