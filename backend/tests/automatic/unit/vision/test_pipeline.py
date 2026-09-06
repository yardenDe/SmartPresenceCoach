from unittest.mock import Mock


def test_process_frame_uses_detector_and_landmark_extractor():
    from vision.vision_pipeline import VisionPipeline

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
        "frame-1",
        pose_mode=True,
        face_mode=False,
        hand_mode=False,
    )
    pipeline.landmark_extractor.filter_landmarks.assert_called_once_with(
        {"raw": "data"}
    )

    assert result["pose"]["nose"]["x"] == 0.5


def test_process_returns_only_frames_with_landmarks():
    from vision.vision_pipeline import VisionPipeline

    pipeline = VisionPipeline(detector=Mock())

    frame_results = {
        "a": {"pose": {"nose": {"x": 0.1, "y": 0.2}}},
        "b": {},
        "c": {"pose": {"nose": {"x": 0.2, "y": 0.2}}},
    }

    pipeline.process_frame = Mock(
        side_effect=lambda frame: frame_results[frame]
    )

    result = pipeline.process(["a", "b", "c"])

    assert result == [
        {"pose": {"nose": {"x": 0.1, "y": 0.2}}},
        {"pose": {"nose": {"x": 0.2, "y": 0.2}}},
    ]
    assert pipeline.process_frame.call_count == 3


def test_process_returns_empty_list_when_no_frames_have_landmarks():
    from vision.vision_pipeline import VisionPipeline

    pipeline = VisionPipeline(detector=Mock())
    pipeline.process_frame = Mock(return_value={})

    result = pipeline.process(["a", "b"])

    assert result == []
    assert pipeline.process_frame.call_count == 2
