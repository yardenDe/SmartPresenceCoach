from statistics import mean
from typing import Any


def clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    return max(min_value, min(max_value, value))


def round_score(value: float, digits: int = 2) -> float:
    return round(value, digits)


def clamp_score(value: float) -> float:
    return round_score(clamp(value, 0.0, 100.0))


def average(values: list[float]) -> float:
    if not values:
        return 0.0
    return mean(values)


def variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    avg = average(values)
    return sum((value - avg) ** 2 for value in values) / len(values)


def standard_deviation(values: list[float]) -> float:
    return variance(values) ** 0.5


def difference(value_a: float, value_b: float) -> float:
    return abs(value_a - value_b)


def point_exists(data: dict[str, Any] | None, point_name: str) -> bool:
    return bool(data and data.get(point_name) is not None)


def points_exist(data: dict[str, Any] | None, *point_names: str) -> bool:
    return all(point_exists(data, point_name) for point_name in point_names)


def point_distance(point_a: dict[str, float], point_b: dict[str, float]) -> float:
    return abs(point_a["x"] - point_b["x"]) + abs(point_a["y"] - point_b["y"])


def axis_distance(point_a: dict[str, float], point_b: dict[str, float], axis: str) -> float:
    return abs(point_a[axis] - point_b[axis])


def absolute_axis_distance(point_a: dict[str, float], point_b: dict[str, float], axis: str) -> float:
    return axis_distance(point_a, point_b, axis)


def midpoint(point_a: dict[str, float], point_b: dict[str, float]) -> dict[str, float]:
    return {
        "x": (point_a["x"] + point_b["x"]) / 2,
        "y": (point_a["y"] + point_b["y"]) / 2,
    }


def ratio(value_a: float, value_b: float, epsilon: float = 1e-6) -> float:
    return value_a / (value_b + epsilon)


def normalize_inverse(raw_value: float, scale: float, max_score: float = 100.0) -> float:
    return clamp_score(max_score - (raw_value * scale))


def normalize_direct(raw_value: float, scale: float, max_score: float = 100.0) -> float:
    return clamp_score(raw_value * scale)


def weighted_average(weighted_values: list[tuple[float, float]]) -> float:
    if not weighted_values:
        return 0.0

    total_weight = sum(weight for _, weight in weighted_values)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(value * weight for value, weight in weighted_values)
    return weighted_sum / total_weight
