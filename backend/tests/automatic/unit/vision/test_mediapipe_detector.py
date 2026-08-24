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

    face_landmarker = make_landmarker_class()
    pose_landmarker = make_landmarker_class()
    hand_landmarker = make_landmarker_class()

    monkeypatch.setattr(python, "BaseOptions", FakeBaseOptions, raising=False)
    monkeypatch.setattr(vision, "FaceLandmarker", face_landmarker, raising=False)
    monkeypatch.setattr(vision, "FaceLandmarkerOptions", FakeOptions, raising=False)
    monkeypatch.setattr(vision, "PoseLandmarker", pose_landmarker, raising=False)
    monkeypatch.setattr(vision, "PoseLandmarkerOptions", FakeOptions, raising=False)
    monkeypatch.setattr(vision, "HandLandmarker", hand_landmarker, raising=False)
    monkeypatch.setattr(vision, "HandLandmarkerOptions", FakeOptions, raising=False)

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

    settings = SimpleNamespace(
        MEDIAPIPE_MODEL_PATH="/models",
        MEDIAPIPE_RUNNING_MODE="IMAGE",
        FACE_LANDMARKER_MODEL="face_landmarker.task",
        POSE_LANDMARKER_MODEL="pose_landmarker.task",
        HAND_LANDMARKER_MODEL="hand_landmarker.task",
    )
    monkeypatch.setattr(module, "get_settings", lambda: settings)

    return module


def test_init_does_not_load_any_model(detector_module):
    detector = detector_module.MediaPipeDetector()

    assert detector.face_detector is None
    assert detector.pose_detector is None
    assert detector.hand_detector is None

    detector_module.FaceLandmarker.create_from_options.assert_not_called()
    detector_module.PoseLandmarker.create_from_options.assert_not_called()
    detector_module.HandLandmarker.create_from_options.assert_not_called()


def test_pose_is_loaded_only_when_requested(detector_module):
    pose_instance = MagicMock()
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    detector = detector_module.MediaPipeDetector()

    loaded = detector._get_pose_detector()

    assert loaded is pose_instance
    assert detector.pose_detector is pose_instance
    detector_module.PoseLandmarker.create_from_options.assert_called_once()
    detector_module.FaceLandmarker.create_from_options.assert_not_called()
    detector_module.HandLandmarker.create_from_options.assert_not_called()


def test_model_is_loaded_only_once(detector_module):
    pose_instance = MagicMock()
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    detector = detector_module.MediaPipeDetector()

    first = detector._get_pose_detector()
    second = detector._get_pose_detector()

    assert first is second is pose_instance
    detector_module.PoseLandmarker.create_from_options.assert_called_once()


def test_each_model_is_loaded_independently(detector_module):
    face_instance = MagicMock()
    hand_instance = MagicMock()
    detector_module.FaceLandmarker.create_from_options.return_value = face_instance
    detector_module.HandLandmarker.create_from_options.return_value = hand_instance

    detector = detector_module.MediaPipeDetector()

    detector._get_face_detector()

    assert detector.face_detector is face_instance
    assert detector.pose_detector is None
    assert detector.hand_detector is None

    detector._get_hand_detector()

    assert detector.hand_detector is hand_instance
    assert detector.pose_detector is None
    detector_module.FaceLandmarker.create_from_options.assert_called_once()
    detector_module.HandLandmarker.create_from_options.assert_called_once()
    detector_module.PoseLandmarker.create_from_options.assert_not_called()


def test_detect_loads_only_enabled_models(detector_module, monkeypatch):
    pose_instance = MagicMock()
    pose_instance.detect.return_value = "pose-result"
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    monkeypatch.setattr(
        detector_module.cv2,
        "cvtColor",
        lambda image, _conversion: image,
    )

    detector = detector_module.MediaPipeDetector()
    result = detector.detect(
        image="frame",
        pose_mode=True,
        face_mode=False,
        hand_mode=False,
    )

    assert result == {"pose_landmarks": "pose-result"}
    detector_module.PoseLandmarker.create_from_options.assert_called_once()
    detector_module.FaceLandmarker.create_from_options.assert_not_called()
    detector_module.HandLandmarker.create_from_options.assert_not_called()
    pose_instance.detect.assert_called_once()


def test_model_path_is_passed_to_mediapipe(detector_module):
    pose_instance = MagicMock()
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    detector = detector_module.MediaPipeDetector()
    detector._get_pose_detector()

    options = detector_module.PoseLandmarker.create_from_options.call_args.args[0]
    assert options.base_options.model_asset_path == "/models/pose_landmarker.task"
    assert options.running_mode == "IMAGE"


def test_close_closes_only_loaded_models(detector_module):
    face_instance = MagicMock()
    pose_instance = MagicMock()
    detector_module.FaceLandmarker.create_from_options.return_value = face_instance
    detector_module.PoseLandmarker.create_from_options.return_value = pose_instance

    detector = detector_module.MediaPipeDetector()
    detector._get_face_detector()
    detector._get_pose_detector()

    detector.close()

    face_instance.close.assert_called_once()
    pose_instance.close.assert_called_once()
    detector_module.HandLandmarker.create_from_options.assert_not_called()


def test_loading_error_is_propagated(detector_module):
    detector_module.PoseLandmarker.create_from_options.side_effect = RuntimeError(
        "failed to load pose model"
    )

    detector = detector_module.MediaPipeDetector()

    with pytest.raises(RuntimeError, match="failed to load pose model"):
        detector._get_pose_detector()

    assert detector.pose_detector is None
