from types import SimpleNamespace
from unittest.mock import Mock, call

from vision.config import FrameLandmarks, Landmark


def test_process_returns_only_frames_with_landmarks():
    from vision.vision_pipeline import VisionPipeline

    detector = Mock()
    poses = [object(), object(), object()]
    detector.detect.side_effect = poses
    pipeline = VisionPipeline(detector=detector)
    first = FrameLandmarks(nose=Landmark(x=0.1, y=0.2))
    last = FrameLandmarks(nose=Landmark(x=0.2, y=0.2))
    pipeline._extract_landmarks = Mock(side_effect=[first, None, last])

    assert pipeline.process(["a", "b", "c"]) == [first, last]
    assert detector.detect.call_args_list == [call("a"), call("b"), call("c")]
    assert pipeline._extract_landmarks.call_args_list == [call(pose) for pose in poses]


def test_process_returns_empty_list_when_no_frames_have_landmarks():
    from vision.vision_pipeline import VisionPipeline

    detector = Mock()
    detector.detect.return_value = SimpleNamespace(pose_landmarks=[])
    pipeline = VisionPipeline(detector=detector)

    assert pipeline.process(["a", "b"]) == []
    assert detector.detect.call_count == 2


def test_process_empty_chunk_does_not_call_detector():
    from vision.vision_pipeline import VisionPipeline

    detector = Mock()
    pipeline = VisionPipeline(detector=detector)

    assert pipeline.process([]) == []
    detector.detect.assert_not_called()
