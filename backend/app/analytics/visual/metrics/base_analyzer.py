from abc import ABC, abstractmethod
from typing import Any

from analytics.math_utils import average_available, average_point_motion, axis_distance


class BaseAnalyzer(ABC):
    """Base class for visual metric analyzers."""

    @staticmethod
    def _has_point(data: dict[str, Any] | None, point_name: str) -> bool:
        return bool(data and data.get(point_name) is not None)

    @classmethod
    def _has_points(cls, data: dict[str, Any] | None, *point_names: str) -> bool:
        return all(cls._has_point(data, point_name) for point_name in point_names)

    @classmethod
    def _collect_points(
        cls,
        frames: list[dict[str, Any]],
        source: str,
        point_name: str,
    ) -> list[dict[str, float]]:
        points = []

        for frame in frames:
            source_data = frame.get(source)
            if cls._has_points(source_data, point_name):
                points.append(source_data[point_name])

        return points

    @classmethod
    def _collect_axis_distances(
        cls,
        frames: list[dict[str, Any]],
        source: str,
        point_a_name: str,
        point_b_name: str,
        axis: str,
    ) -> list[float]:
        distances = []

        for frame in frames:
            source_data = frame.get(source)
            if cls._has_points(source_data, point_a_name, point_b_name):
                distances.append(axis_distance(source_data[point_a_name], source_data[point_b_name], axis))

        return distances

    @classmethod
    def _average_named_point_motion(
        cls,
        frames: list[dict[str, Any]],
        source: str,
        point_names: list[str],
    ) -> float | None:
        motions = []

        for point_name in point_names:
            points = cls._collect_points(frames, source, point_name)
            motion = average_point_motion(points)
            if motion is not None:
                motions.append(motion)

        return average_available(motions)

    @abstractmethod
    def analyze(self, frames: list[dict[str, Any]]) -> float | None:
        pass
