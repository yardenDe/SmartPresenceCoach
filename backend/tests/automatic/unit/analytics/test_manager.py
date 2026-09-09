from unittest.mock import Mock

import pytest

from analytics.manager import AnalyticsManager
from analytics.visual.manager import VisualAnalyticsManager
from core.exceptions import AnalyticsProcessingError
from schemas.analysis import AudioMetrics, VisualMetrics


def test_visual_analysis_returns_raw_metrics(sample_frame):
    result = VisualAnalyticsManager().analyze(
        [sample_frame(), sample_frame(0.005), sample_frame(0.01)]
    )
    assert set(result.model_dump(exclude_none=True)) == set(VisualMetrics.model_fields)
    assert result.face_direction == pytest.approx(0.0)
    assert result.shoulder_tilt == pytest.approx(0.0)
    assert result.movement_amount > 0
    assert result.movement_variation == pytest.approx(0.0, abs=1e-10)


def test_empty_input_raises_analytics_error():
    with pytest.raises(AnalyticsProcessingError):
        VisualAnalyticsManager().analyze([])


def test_analytics_manager_delegates_to_visual_and_audio(sample_frame):
    visual = Mock()
    visual.analyze.return_value = VisualMetrics(face_direction=4.0)
    audio = Mock()
    audio.analyze.return_value = AudioMetrics(average_volume=-19.0)
    manager = AnalyticsManager(visual=visual, audio=audio)
    landmarks = [sample_frame()]
    audio_features = object()

    result = manager.analyze(landmarks=landmarks, audio_features=audio_features)

    visual.analyze.assert_called_once_with(landmarks)
    audio.analyze.assert_called_once_with(audio_features)
    assert result.visual is visual.analyze.return_value
    assert result.audio is audio.analyze.return_value


def test_analytics_manager_skips_missing_inputs():
    visual, audio = Mock(), Mock()
    result = AnalyticsManager(visual, audio).analyze()
    assert result.visual is None and result.audio is None
    visual.analyze.assert_not_called()
    audio.analyze.assert_not_called()
