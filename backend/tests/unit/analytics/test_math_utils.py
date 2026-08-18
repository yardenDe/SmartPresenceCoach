import pytest


def test_score_helpers():
    from analytics import math_utils as math

    assert math.clamp(120) == 100.0
    assert math.clamp(-20) == 0.0
    assert math.clamp_score(55.678) == 55.68
    assert math.average([10, 20, 30]) == 20
    assert math.average([]) == 0.0
    assert math.weighted_average([(80, 0.75), (40, 0.25)]) == 70


def test_point_helpers():
    from analytics import math_utils as math

    a = {"x": 0.1, "y": 0.2}
    b = {"x": 0.4, "y": 0.6}

    assert math.point_distance(a, b) == pytest.approx(0.5)
    assert math.axis_distance(a, b, "x") == pytest.approx(0.3)
    assert math.midpoint(a, b) == pytest.approx({"x": 0.25, "y": 0.4})
    assert math.average_absolute_change([1.0, 3.0, 2.0]) == pytest.approx(1.5)
