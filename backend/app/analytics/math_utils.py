from analytics.config import AnalyticsConfig


def clamp_score(value: float) -> float:
    return round(
        max(AnalyticsConfig.MIN_SCORE, min(AnalyticsConfig.MAX_SCORE, value)),
        2,
    )


def point_exists(data, point_name: str) -> bool:
    return bool(data and data.get(point_name) is not None)


def points_exist(data, *point_names: str) -> bool:
    return all(point_exists(data, point_name) for point_name in point_names)


def absolute_axis_distance(point_a: dict, point_b: dict, axis: str) -> float:
    return abs(point_a[axis] - point_b[axis])


def point_distance(point_a: dict, point_b: dict) -> float:
    return abs(point_a["x"] - point_b["x"]) + abs(point_a["y"] - point_b["y"])


def midpoint(point_a: dict, point_b: dict) -> dict:
    return {
        "x": (point_a["x"] + point_b["x"]) / 2,
        "y": (point_a["y"] + point_b["y"]) / 2,
    }
