from unittest.mock import Mock

import numpy as np
import pytest

from analytics.score_calculator import ScoreCalculator
from models.snapshot import Snapshot
from schemas.analysis import Analysis, AudioMetrics, VisualMetrics
from services.analysis_service import AnalysisService


@pytest.mark.parametrize("kind", ["visual", "audio", "both", "empty"])
def test_process_returns_complete_snapshot_without_persisting(kind):
    analytics = Mock()
    analytics.analyze.return_value = Analysis(
        visual=VisualMetrics(face_direction=0.0) if kind in {"visual", "both"} else None,
        audio=AudioMetrics(average_volume=-19.0, transcript="Hello") if kind in {"audio", "both"} else None,
    )
    vision = Mock()
    vision.process.return_value = [{"nose": {"x": 0.5, "y": 0.2}}]
    audio_pipeline = Mock()
    service = AnalysisService(analytics, vision, ScoreCalculator(), audio_pipeline)
    frames = [object()]
    audio = np.array([0.1])

    snapshot = service.process(session_id=25, timestamp=3.0, frames=frames, audio=audio)

    vision.process.assert_called_once_with(frames)
    audio_pipeline.process.assert_called_once_with(audio)
    analytics.analyze.assert_called_once_with(
        landmarks=vision.process.return_value,
        audio_features=audio_pipeline.process.return_value,
    )
    if kind == "empty":
        assert snapshot is None
        return
    assert isinstance(snapshot, Snapshot)
    assert snapshot.id is None
    assert snapshot.session_id == 25
    assert snapshot.timestamp == 3.0
    assert snapshot.face_direction == (0.0 if kind in {"visual", "both"} else None)
    assert snapshot.average_volume == (-19.0 if kind in {"audio", "both"} else None)
    assert snapshot.transcript == ("Hello" if kind in {"audio", "both"} else None)
    assert service.generate_scores(snapshot).overall is not None


def test_empty_snapshot_has_no_scores():
    assert ScoreCalculator().calculate(Snapshot(session_id=25, timestamp=0.0)) is None
