from math import atan2, degrees
from vision.config import FrameLandmarks

from analytics.math_utils import average_available
from analytics.visual.metrics.base_analyzer import BaseAnalyzer


class FaceDirectionAnalyzer(BaseAnalyzer):
    def _calculate_direction(
        self,
        landmarks: FrameLandmarks,
    ) -> float | None:
        if not self._has_point(landmarks, "nose"):
            return None

        face_center = self._face_center(landmarks)
        face_width = self._face_width(landmarks)

        if face_center is None or face_width is None or face_width <= 0:
            return None

        horizontal_offset = abs(
            landmarks.nose.x - face_center.x
        )

        return degrees(atan2(horizontal_offset, face_width))

    def analyze(self, frames: list[FrameLandmarks]) -> float | None:
        directions = [
            direction
            for landmarks in frames
            if (direction := self._calculate_direction(landmarks)) is not None
        ]

        return average_available(directions)
