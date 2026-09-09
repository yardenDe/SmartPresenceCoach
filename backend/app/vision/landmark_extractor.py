from typing import Any

from core.exceptions import VisionProcessingError
from core.logger import get_logger
from vision.config import MEDIAPIPE_LANDMARKS

logger = get_logger("app.vision.landmarks")


class LandmarkExtractor:

    def filter_landmarks(
        self,
        pose_result: Any,
    ) -> dict[str, dict[str, float]]:
        try:
            if not pose_result or not getattr(
                pose_result,
                "pose_landmarks",
                None,
            ):
                return {}

            landmarks = pose_result.pose_landmarks[0]
            extracted = {}

            for idx, name in MEDIAPIPE_LANDMARKS.items():
                if idx < len(landmarks):
                    extracted[name] = {
                        "x": landmarks[idx].x,
                        "y": landmarks[idx].y,
                    }

            logger.debug(
                "event=landmarks.extract.done has_pose=%s",
                bool(extracted),
            )

            return extracted

        except Exception:
            logger.exception(
                "event=landmarks.extract.failed"
            )
            raise VisionProcessingError()
