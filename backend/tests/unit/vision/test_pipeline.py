from unittest.mock import Mock


def test_process_frame_uses_detector_and_landmark_extractor():
    from vision.pipeline import VisionPipeline

    detector = Mock()
    detector.detect.return_value = {"raw": "data"}
    pipeline = VisionPipeline(detector=detector)
    pipeline.landmark_extractor = Mock()
    pipeline.landmark_extractor.filter_landmarks.return_value = {
        "pose": {"nose": {"x": 0.5, "y": 0.2}},
        "face": None,
        "hands": [],
    }

    result = pipeline.process_frame("frame-1")

    detector.detect.assert_called_once_with(
        "frame-1", pose_mode=True, face_mode=False, hand_mode=False
    )
    pipeline.landmark_extractor.filter_landmarks.assert_called_once_with({"raw": "data"})
    assert result["pose"]["nose"]["x"] == 0.5


def test_pipeline_yields_one_landmark_list_per_chunk(monkeypatch):
    import vision.pipeline as pipeline_module

    class FakeVideoExtractor:
        def __init__(self, video_path):
            assert video_path == "demo.mp4"

        def get_chunks(self, chunk_sec, target_fps):
            assert chunk_sec > 0
            assert target_fps > 0
            yield ["a", "b"]
            yield ["c"]

    pipeline = pipeline_module.VisionPipeline(detector=Mock())
    pipeline.process_frame = Mock(
        side_effect=[
            {"pose": {"nose": {"x": 0.1, "y": 0.2}}},
            {},
            {"pose": {"nose": {"x": 0.2, "y": 0.2}}},
        ]
    )
    monkeypatch.setattr(pipeline_module, "VideoExtractor", FakeVideoExtractor)

    chunks = list(pipeline.pipeline(video_path="demo.mp4"))

    assert [len(chunk) for chunk in chunks] == [1, 1]
    assert pipeline.process_frame.call_count == 3
