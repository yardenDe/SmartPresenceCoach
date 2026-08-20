import pytest


def test_run_full_analysis_returns_metrics_and_overall(sample_frame):
    from analytics.manager import AnalyticsManager

    result = AnalyticsManager().run_full_analysis(
        [sample_frame(), sample_frame(0.005), sample_frame(0.01)]
    )

    assert set(result) == {
        "focus", "posture", "engagement", "presence", "composure", "overall"
    }
    for score in result.values():
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    metric_values = [
        result["focus"], result["posture"], result["engagement"],
        result["presence"], result["composure"],
    ]
    assert result["overall"] == pytest.approx(sum(metric_values) / len(metric_values))


def test_empty_input_raises_analytics_error():
    from analytics.manager import AnalyticsManager
    from core.exceptions import AnalyticsProcessingError

    with pytest.raises(AnalyticsProcessingError):
        AnalyticsManager().run_full_analysis([])
