from unittest.mock import Mock


def test_process_chunk_builds_analysis(sample_frame):
    from schemas.analysis import Analysis, VisualAnalysis
    from services.analysis_service import AnalysisService

    analytics = Mock()
    expected = Analysis(
        visual=VisualAnalysis(focus=80.0, posture=90.0, overall=85.0),
    )
    analytics.analyze.return_value = expected
    landmarks = [sample_frame(), sample_frame(0.01)]
    vision_pipeline = Mock()
    vision_pipeline.process.return_value = landmarks
    service = AnalysisService(
        analytics=analytics,
        vision_pipeline=vision_pipeline,
    )

    chunk_frames = [object(), object()]
    result = service.process(frames=chunk_frames)

    assert result is expected
    vision_pipeline.process.assert_called_once_with(chunk_frames)
    analytics.analyze.assert_called_once_with(
        landmarks=landmarks,
        audio_features=None,
    )
