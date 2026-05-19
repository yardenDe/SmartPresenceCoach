from math import atan2, degrees, hypot
from statistics import mean

from analytics.config import AnalyticsConfig

Point = dict[str, float]


def clamp(
    value: float,
    min_value: float = AnalyticsConfig.MIN_SCORE,
    max_value: float = AnalyticsConfig.MAX_SCORE,
) -> float:
    return max(min_value, min(max_value, value))


def clamp_score(value: float) -> float:
    return round(clamp(value), 2)


def average(values: list[float]) -> float:
    return mean(values) if values else 0.0


def average_available(values: list[float]) -> float | None:
    return average(values) if values else None


def average_score(values: list[float]) -> float | None:
    avg = average_available(values)
    return clamp_score(avg) if avg is not None else None


def variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    avg = average(values)
    return average([(value - avg) ** 2 for value in values])


def average_absolute_change(values: list[float]) -> float | None:
    if len(values) < 2:
        return None

    changes = [
        abs(values[index] - values[index - 1])
        for index in range(1, len(values))
    ]
    return average(changes)


def second_half_average_increase(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    midpoint_index = len(values) // 2
    first_half = values[:midpoint_index]
    second_half = values[midpoint_index:]
    return max(0.0, average(second_half) - average(first_half))


def weighted_average(weighted_values: list[tuple[float, float] | None]) -> float | None:
    values = [weighted_value for weighted_value in weighted_values if weighted_value is not None]
    if not values:
        return None

    total_weight = sum(weight for _, weight in values)
    if total_weight == 0:
        return None

    return sum(value * weight for value, weight in values) / total_weight


def point_distance(point_a: Point, point_b: Point) -> float:
    return hypot(point_a["x"] - point_b["x"], point_a["y"] - point_b["y"])


def axis_distance(point_a: Point, point_b: Point, axis: str) -> float:
    return abs(point_a[axis] - point_b[axis])


def average_point_motion(points: list[Point]) -> float | None:
    if len(points) < 2:
        return None

    distances = [
        point_distance(points[index], points[index - 1])
        for index in range(1, len(points))
    ]
    return average(distances)


def point_variance(points: list[Point]) -> float:
    return variance([point["x"] for point in points]) + variance([point["y"] for point in points])


def midpoint(point_a: Point, point_b: Point) -> Point:
    return {
        "x": (point_a["x"] + point_b["x"]) / 2,
        "y": (point_a["y"] + point_b["y"]) / 2,
    }


def point_in_bounds(point: Point, top: Point, bottom: Point, left: Point, right: Point) -> bool:
    return (
        min(left["x"], right["x"]) <= point["x"] <= max(left["x"], right["x"])
        and min(top["y"], bottom["y"]) <= point["y"] <= max(top["y"], bottom["y"])
    )


def line_angle_degrees(point_a: Point, point_b: Point) -> float:
    y_delta = point_b["y"] - point_a["y"]
    x_delta = point_b["x"] - point_a["x"]
    return abs(degrees(atan2(y_delta, x_delta)))


def normalize_inverse(
    raw_value: float,
    scale: float,
    max_score: float = AnalyticsConfig.DEFAULT_SCORE,
) -> float:
    return clamp_score(max_score - (raw_value * scale))


def normalize_direct(
    raw_value: float,
    scale: float,
) -> float:
    return clamp_score(raw_value * scale)
