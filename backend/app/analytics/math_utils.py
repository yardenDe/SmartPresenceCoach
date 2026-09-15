from math import atan2, degrees, hypot
from statistics import mean

from analytics.config import MAX_SCORE, MIN_SCORE, MetricDefinition

from vision.config import Landmark


def clamp_score(
    value: float,
    min_value: float = MIN_SCORE,
    max_value: float = MAX_SCORE,
) -> float:
    if value < min_value:
        return min_value

    if value > max_value:
        return max_value
    return value


def normalize_metric(
    value: float | None,
    definition: MetricDefinition,
) -> float | None:
    if value is None:
        return None

    if definition.target_min <= value <= definition.target_max:
        return 0.0

    if value < definition.target_min:
        if definition.target_min == definition.min_value:
            return 100.0

        score = 100.0 * (
            (value - definition.min_value)
            / (definition.target_min - definition.min_value)
        )
    else:
        if definition.target_max == definition.max_value:
            return 0.0

        score = 100.0 * (
            (definition.max_value - value)
            / (definition.max_value - definition.target_max)
        )

    return clamp_score(score)


def average_available(values: list[float]) -> float | None:
    return mean(values) if values else None


def average_scores(*values: float | None) -> float | None:
    result = average_available([
        value
        for value in values
        if value is not None
    ])
    return clamp_score(result) if result is not None else None


def point_distance(point_a: Landmark, point_b: Landmark) -> float:
    return hypot(point_a.x - point_b.x, point_a.y - point_b.y)


def axis_distance(point_a: Landmark, point_b: Landmark, axis: str) -> float:
    return abs(getattr(point_a, axis) - getattr(point_b, axis))


def midpoint(point_a: Landmark, point_b: Landmark) -> Landmark:
    return Landmark(
        x=(point_a.x + point_b.x) / 2,
        y=(point_a.y + point_b.y) / 2,
    )


def line_angle_degrees(point_a: Landmark, point_b: Landmark) -> float:
    y_delta = point_b.y - point_a.y
    x_delta = point_b.x - point_a.x
    return abs(degrees(atan2(y_delta, x_delta)))
