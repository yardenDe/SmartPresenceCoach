from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def detector_module(monkeypatch):
    """Load the real detector module while replacing MediaPipe with lightweight fakes."""
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    class FakeBaseOptions:
        def __init__(self, model_asset_path: str):
            self.model_asset_path = model_asset_path

    class FakeOptions:
        def __init__(self, base_options, running_mode):
            self.base_options = base_options
            self.running_mode = running_mode

    def make_landmarker_class():
        class FakeLandmarker:
            create_from_options = MagicMock()

        return FakeLandmarker

    pose_landmarker = make_landmarker_class()

    monkeypatch.setattr(python, "BaseOptions", FakeBaseOptions, raising=False)
    monkeypatch.setattr(vision, "PoseLandmarker", pose_landmarker, raising=False)
    monkeypatch.setattr(vision, "PoseLandmarkerOptions", FakeOptions, raising=False)
    monkeypatch.setattr(vision, "PoseLandmarkerResult", SimpleNamespace, raising=False)

    monkeypatch.setattr(mp, "ImageFormat", SimpleNamespace(SRGB="SRGB"), raising=False)
    monkeypatch.setattr(
        mp,
        "Image",
        lambda image_format, data: SimpleNamespace(
            image_format=image_format,
            data=data,
        ),
        raising=False,
    )

    module_path = (
        Path(__file__).resolve().parents[4]
        / "app"
        / "vision"
        / "mediapipe_detector.py"
    )
    spec = importlib.util.spec_from_file_location(
        "real_mediapipe_detector_for_tests",
        module_path,
    )
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def test_init_does_not_load_any_model(detector_module):
    detector = detector_module.MediaPipeDetector(
        model_path="/models",
        model_name="pose_landmarker.task",
        running_mode=detector_module.RunningMode.IMAGE,
    )

    assert detector.pose_detector is None

    detector_module.PoseLandmarker.create_from_options.assert_not_called()


def test_pose_is_loaded_only_when_requested(detector_module):
    pose_instance = MagicMock()
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    detector = detector_module.MediaPipeDetector(
        model_path="/models",
        model_name="pose_landmarker.task",
        running_mode=detector_module.RunningMode.IMAGE,
    )

    loaded = detector._get_pose_detector()

    assert loaded is pose_instance
    assert detector.pose_detector is pose_instance
    detector_module.PoseLandmarker.create_from_options.assert_called_once()


def test_model_is_loaded_only_once(detector_module):
    pose_instance = MagicMock()
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    detector = detector_module.MediaPipeDetector(
        model_path="/models",
        model_name="pose_landmarker.task",
        running_mode=detector_module.RunningMode.IMAGE,
    )

    first = detector._get_pose_detector()
    second = detector._get_pose_detector()

    assert first is second is pose_instance
    detector_module.PoseLandmarker.create_from_options.assert_called_once()


def test_detect_loads_pose_model(detector_module, monkeypatch):
    pose_instance = MagicMock()
    pose_result = SimpleNamespace(pose_landmarks=[])
    pose_instance.detect.return_value = pose_result
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    monkeypatch.setattr(
        detector_module.cv2,
        "cvtColor",
        lambda image, _conversion: image,
    )

    detector = detector_module.MediaPipeDetector(
        model_path="/models",
        model_name="pose_landmarker.task",
        running_mode=detector_module.RunningMode.IMAGE,
    )
    result = detector.detect(
        image="frame",
    )

    assert result is pose_result
    detector_module.PoseLandmarker.create_from_options.assert_called_once()
    pose_instance.detect.assert_called_once()


def test_model_path_is_passed_to_mediapipe(detector_module):
    pose_instance = MagicMock()
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    detector = detector_module.MediaPipeDetector(
        model_path="/models",
        model_name="pose_landmarker.task",
        running_mode=detector_module.RunningMode.IMAGE,
    )
    detector._get_pose_detector()

    options = detector_module.PoseLandmarker.create_from_options.call_args.args[0]
    assert options.base_options.model_asset_path == str(Path("/models") / "pose_landmarker.task")
    assert options.running_mode == "IMAGE"


def test_close_closes_only_loaded_models(detector_module):
    pose_instance = MagicMock()
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    detector = detector_module.MediaPipeDetector(
        model_path="/models",
        model_name="pose_landmarker.task",
        running_mode=detector_module.RunningMode.IMAGE,
    )
    detector._get_pose_detector()

    detector.close()

    pose_instance.close.assert_called_once()


def test_loading_error_is_propagated(detector_module):
    detector_module.PoseLandmarker.create_from_options.side_effect = RuntimeError(
        "failed to load pose model"
    )

    detector = detector_module.MediaPipeDetector(
        model_path="/models",
        model_name="pose_landmarker.task",
        running_mode=detector_module.RunningMode.IMAGE,
    )

    with pytest.raises(RuntimeError, match="failed to load pose model"):
        detector._get_pose_detector()

    assert detector.pose_detector is None
