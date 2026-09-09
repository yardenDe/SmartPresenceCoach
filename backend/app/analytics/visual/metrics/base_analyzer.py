from abc import ABC, abstractmethod
from typing import Any

from analytics.math_utils import average_available, axis_distance, midpoint, point_distance
from media.config import TARGET_FPS


class BaseAnalyzer(ABC):
    @staticmethod
    def _has_point(data: dict[str, Any] | None, point_name: str) -> bool:
        return bool(data and data.get(point_name) is not None)

    @classmethod
    def _has_points(cls, data: dict[str, Any] | None, *point_names: str) -> bool:
        return all(cls._has_point(data, point_name) for point_name in point_names)

    @classmethod
    def _reference_scale(
        cls,
        landmarks: dict[str, Any],
    ) -> float | None:
        if cls._has_points(landmarks, "left_shoulder", "right_shoulder"):
            scale = point_distance(
                landmarks["left_shoulder"],
                landmarks["right_shoulder"],
            )
            if scale > 0:
                return scale

        if cls._has_points(landmarks, "left_ear", "right_ear"):
            scale = point_distance(
                landmarks["left_ear"],
                landmarks["right_ear"],
            )
            if scale > 0:
                return scale

        if cls._has_points(landmarks, "left_eye_basic", "right_eye_basic"):
            scale = point_distance(
                landmarks["left_eye_basic"],
                landmarks["right_eye_basic"],
            )
            if scale > 0:
                return scale

        return None

    @classmethod
    def _normalized_point_motion(
        cls,
        previous_landmarks: dict[str, Any],
        current_landmarks: dict[str, Any],
        point_names: list[str],
    ) -> float | None:
        previous_scale = cls._reference_scale(previous_landmarks)
        current_scale = cls._reference_scale(current_landmarks)

        scales = [
            scale
            for scale in (previous_scale, current_scale)
            if scale is not None
        ]
        scale = average_available(scales)

        if scale is None or scale <= 0:
            return None

        distances = [
            point_distance(
                previous_landmarks[point_name],
                current_landmarks[point_name],
            ) / scale
            for point_name in point_names
            if cls._has_point(previous_landmarks, point_name)
            and cls._has_point(current_landmarks, point_name)
        ]

        normalized_motion = average_available(distances)
        if normalized_motion is None:
            return None

        return normalized_motion * TARGET_FPS

    @classmethod
    def _normalized_motion_series(
        cls,
        frames: list[dict[str, Any]],
        point_names: list[str],
    ) -> list[float]:
        motions = []

        for index in range(1, len(frames)):
            motion = cls._normalized_point_motion(
                frames[index - 1],
                frames[index],
                point_names,
            )
            if motion is not None:
                motions.append(motion)

        return motions

    @classmethod
    def _face_center(
        cls,
        landmarks: dict[str, Any],
    ) -> dict[str, float] | None:
        if cls._has_points(landmarks, "left_ear", "right_ear"):
            return midpoint(
                landmarks["left_ear"],
                landmarks["right_ear"],
            )

        if cls._has_points(landmarks, "left_eye_basic", "right_eye_basic"):
            return midpoint(
                landmarks["left_eye_basic"],
                landmarks["right_eye_basic"],
            )

        return None

    @classmethod
    def _face_width(
        cls,
        landmarks: dict[str, Any],
    ) -> float | None:
        if cls._has_points(landmarks, "left_ear", "right_ear"):
            return axis_distance(
                landmarks["left_ear"],
                landmarks["right_ear"],
                "x",
            )

        if cls._has_points(landmarks, "left_eye_basic", "right_eye_basic"):
            return axis_distance(
                landmarks["left_eye_basic"],
                landmarks["right_eye_basic"],
                "x",
            )

        return None

    @abstractmethod
    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        pass
