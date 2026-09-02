from unittest.mock import Mock


def test_process_chunk_builds_analysis(sample_frame):
    from services.analysis_service import AnalysisService

    analytics = Mock()
    analytics.run_full_analysis.return_value = {
        "focus": 80.0, "posture": 90.0, "overall": 85.0
    }
    landmarks = [sample_frame(), sample_frame(0.01)]
    vision_pipeline = Mock()
    vision_pipeline.process.return_value = landmarks
    service = AnalysisService(
        analytics=analytics,
        vision_pipeline=vision_pipeline,
    )

    chunk_frames = [object(), object()]
    result = service.process_chunk(
        chunk_frames=chunk_frames,
        chunk_index=2,
        timestamp_offset=5.0,
    )

    assert result == {
        "chunk_index": 2,
        "timestamp": 8.0,
        "frames_count": 2,
        "scores": {"focus": 80.0, "posture": 90.0, "overall": 85.0},
    }
    vision_pipeline.process.assert_called_once_with(chunk_frames)
    analytics.run_full_analysis.assert_called_once()
