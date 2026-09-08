from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from analytics.score_calculator import ScoreCalculator
from core.exceptions import SnapshotsNotFoundError
from models.snapshot import Snapshot
from services.report_service import ReportService


def test_full_report_reads_snapshot_objects_and_preserves_missing_metrics():
    repository = Mock()
    repository.get_by_session.return_value = [
        Snapshot(session_id=25, timestamp=0.0, gaze_direction=0.0, transcript="Hello"),
        Snapshot(session_id=25, timestamp=3.0, gaze_direction=10.0, average_volume=-19.0, transcript="world"),
    ]
    sessions = Mock()
    sessions.require_owned_session.return_value = SimpleNamespace(mode="speech")
    reports = Mock()
    reports.get_by_session.return_value = None
    service = ReportService(sessions, repository, reports, ScoreCalculator())

    report = service.generate_report(user_id=7, session_id=25, full=True)

    repository.get_by_session.assert_called_once_with(25)
    assert report.score_series.timestamps_sec == [0.0, 3.0]
    assert report.metric_series.series["average_volume"] == [None, -19.0]
    assert report.visual_metrics["gaze_direction"].avg == 5.0
    assert report.audio_metrics["average_volume"].avg == -19.0
    assert report.transcript == "Hello world"
    assert report.scores["overall"].avg is not None


def test_report_rejects_session_without_snapshots():
    repository = Mock()
    repository.get_by_session.return_value = []
    service = ReportService(Mock(), repository, Mock(), ScoreCalculator())

    with pytest.raises(SnapshotsNotFoundError):
        service.generate_report(user_id=7, session_id=25, full=False)
