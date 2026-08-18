from unittest.mock import Mock


def test_process_chunk_builds_snapshot_without_running_video_pipeline(sample_frame):
    from services.session_analysis_service import SessionAnalysisService

    analytics = Mock()
    analytics.run_full_analysis.return_value = {
        "focus": 80.0, "posture": 90.0, "overall": 85.0
    }
    session_buffer = Mock()
    session_buffer.should_flush.return_value = False
    repository = Mock()
    service = SessionAnalysisService(
        analytics=analytics,
        detector=Mock(),
        session_buffer=session_buffer,
        snapshot_repository=repository,
    )

    result = service._process_chunk(
        session_id=7,
        chunk_index=2,
        landmarks_list=[sample_frame(), sample_frame(0.01)],
        timestamp_offset=5.0,
    )

    assert result == {
        "session_id": 7,
        "chunk_index": 2,
        "timestamp": 8.0,
        "frames_count": 2,
        "scores": {"focus": 80.0, "posture": 90.0, "overall": 85.0},
    }
    analytics.run_full_analysis.assert_called_once()
    session_buffer.add.assert_called_once_with(
        session_id=7,
        snapshot={
            "focus": 80.0, "posture": 90.0, "overall": 85.0, "timestamp": 8.0
        },
    )
    repository.create_snapshots.assert_not_called()


def test_process_offline_uses_fake_pipeline_and_flushes(monkeypatch, sample_frame):
    import services.session_analysis_service as service_module

    class FakePipeline:
        last_instance = None

        def __init__(self, detector):
            self.detector = detector
            self.closed = False
            FakePipeline.last_instance = self

        def pipline(self, video_path):
            assert video_path == "video.mp4"
            yield [sample_frame()]
            yield []
            yield [sample_frame(), sample_frame(0.01)]

        def close(self):
            self.closed = True

    monkeypatch.setattr(service_module, "VisionPipeline", FakePipeline)
    analytics = Mock()
    analytics.run_full_analysis.return_value = {"focus": 80.0, "overall": 80.0}
    session_buffer = Mock()
    session_buffer.should_flush.return_value = False
    session_buffer.flush.return_value = [{"focus": 80.0, "overall": 80.0, "timestamp": 0.0}]
    repository = Mock()
    service = service_module.SessionAnalysisService(
        analytics=analytics,
        detector=Mock(),
        session_buffer=session_buffer,
        snapshot_repository=repository,
    )

    response = service.process_offline(video_path="video.mp4", session_id=12)

    assert response.session_id == 12
    assert response.status == "success"
    assert analytics.run_full_analysis.call_count == 2
    session_buffer.flush.assert_called_once_with(12)
    repository.create_snapshots.assert_called_once()
    assert FakePipeline.last_instance.closed is True
