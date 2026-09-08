from typing import Any

from core.exceptions import VisionProcessingError
from core.logger import get_logger
from vision.config import MEDIAPIPE_POSE_MAP

logger = get_logger("app.vision.landmarks")


class LandmarkExtractor:

    def filter_landmarks(self, pose_result: Any) -> dict[str, dict[str, float]]:
       
        try:
            result = self._extract_pose(pose_result)
        except Exception:
            logger.exception("event=landmarks.extract.failed")
            raise VisionProcessingError()

        logger.debug(
            "event=landmarks.extract.done has_pose=%s",
            bool(result),
        )

        return result

    def _extract_pose(self, pose_data: Any) -> dict[str, dict[str, float]]:

        if not pose_data or not getattr(pose_data, "pose_landmarks", None):
            return {}

        pose_points = pose_data.pose_landmarks[0]
        extracted = {}

        for idx, name in MEDIAPIPE_POSE_MAP.items():
            if idx < len(pose_points):
                extracted[name] = {
                    "x": pose_points[idx].x,
                    "y": pose_points[idx].y
                }

        return extracted
