from math import atan2, degrees, hypot
from statistics import mean

from analytics.config import MAX_SCORE, MIN_SCORE, MetricDefinition

Point = dict[str, float]


def clamp(
    value: float,
    min_value: float = MIN_SCORE,
    max_value: float = MAX_SCORE,
) -> float:
    return max(min_value, min(max_value, value))


def clamp_score(value: float) -> float:
    return round(clamp(value), 2)


def normalize_metric(
    value: float | None,
    definition: MetricDefinition,
) -> float | None:
    if value is None:
        return None

    if definition.target_min <= value <= definition.target_max:
        return 100.0

    if value < definition.target_min:
        if definition.target_min == definition.min_value:
            return 100.0

        score = 100.0 * (
            (value - definition.min_value)
            / (definition.target_min - definition.min_value)
        )
    else:
        if definition.target_max == definition.max_value:
            return 100.0

        score = 100.0 * (
            (definition.max_value - value)
            / (definition.max_value - definition.target_max)
        )

    return clamp_score(score)


def average(values: list[float]) -> float:
    return mean(values) if values else 0.0


def average_available(values: list[float]) -> float | None:
    return average(values) if values else None


def average_score(values: list[float]) -> float | None:
    result = average_available(values)
    return clamp_score(result) if result is not None else None


def average_scores(*values: float | None) -> float | None:
    return average_score([
        value
        for value in values
        if value is not None
    ])


def point_distance(point_a: Point, point_b: Point) -> float:
    return hypot(point_a["x"] - point_b["x"], point_a["y"] - point_b["y"])


def axis_distance(point_a: Point, point_b: Point, axis: str) -> float:
    return abs(point_a[axis] - point_b[axis])


def midpoint(point_a: Point, point_b: Point) -> Point:
    return {
        "x": (point_a["x"] + point_b["x"]) / 2,
        "y": (point_a["y"] + point_b["y"]) / 2,
    }


def line_angle_degrees(point_a: Point, point_b: Point) -> float:
    y_delta = point_b["y"] - point_a["y"]
    x_delta = point_b["x"] - point_a["x"]
    return abs(degrees(atan2(y_delta, x_delta)))
