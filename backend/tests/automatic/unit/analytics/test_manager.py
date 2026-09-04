import pytest


def test_run_full_analysis_returns_metrics_and_overall(sample_frame):
    from analytics.visual.manager import VisualAnalyticsManager

    result = VisualAnalyticsManager().run_full_analysis(
        [sample_frame(), sample_frame(0.005), sample_frame(0.01)]
    )

    values = result.model_dump(exclude_none=True)

    assert set(values) == {
        "focus", "posture", "engagement", "presence", "composure", "overall"
    }
    for score in values.values():
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    metric_values = [
        result.focus, result.posture, result.engagement,
        result.presence, result.composure,
    ]
    assert result.overall == pytest.approx(sum(metric_values) / len(metric_values))


def test_empty_input_raises_analytics_error():
    from analytics.visual.manager import VisualAnalyticsManager
    from core.exceptions import AnalyticsProcessingError

    with pytest.raises(AnalyticsProcessingError):
        VisualAnalyticsManager().run_full_analysis([])


def test_analytics_manager_delegates_to_visual_and_audio():
    from unittest.mock import Mock

    from analytics.manager import AnalyticsManager

    visual = Mock()
    audio = Mock()
    manager = AnalyticsManager(visual=visual, audio=audio)
    landmarks = [{"pose": {}}]
    audio_features = object()

    manager.analyze_visual(landmarks)
    manager.analyze_audio(audio_features)

    visual.run_full_analysis.assert_called_once_with(landmarks)
    audio.run_full_analysis.assert_called_once_with(audio_features)
