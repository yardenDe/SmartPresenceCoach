"""Shared test configuration and fixtures for backend unit tests."""

from __future__ import annotations

import os
import sys
import types
from enum import Enum

import pytest


os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("MEDIAPIPE_RUNNING_MODE", "IMAGE")


class DummyMediaPipeDetector:
    """Lightweight stand-in so unit tests never initialize MediaPipe."""


class DummyRunningMode(str, Enum):
    IMAGE = "IMAGE"


mediapipe_module = types.ModuleType("mediapipe")
tasks_module = types.ModuleType("mediapipe.tasks")
python_module = types.ModuleType("mediapipe.tasks.python")
vision_module = types.ModuleType("mediapipe.tasks.python.vision")
vision_module.RunningMode = DummyRunningMode
vision_module.PoseLandmark = Enum("PoseLandmark", {"NOSE": 0})
vision_module.PoseLandmarkerResult = types.SimpleNamespace

sys.modules.setdefault("mediapipe", mediapipe_module)
sys.modules.setdefault("mediapipe.tasks", tasks_module)
sys.modules.setdefault("mediapipe.tasks.python", python_module)
sys.modules.setdefault("mediapipe.tasks.python.vision", vision_module)
sys.modules["vision.mediapipe_detector"] = types.SimpleNamespace(
    MediaPipeDetector=DummyMediaPipeDetector
)


def build_sample_frame(offset: float = 0.0) -> dict:
    return {

        "nose": {"x": 0.50 + offset, "y": 0.20},
        "left_ear": {"x": 0.38 + offset, "y": 0.22},
        "right_ear": {"x": 0.62 + offset, "y": 0.22},
        "left_shoulder": {"x": 0.35 + offset, "y": 0.40},
        "right_shoulder": {"x": 0.65 + offset, "y": 0.40},
        "left_elbow": {"x": 0.25 + offset, "y": 0.55},
        "right_elbow": {"x": 0.75 + offset, "y": 0.55},
        "left_wrist_basic": {"x": 0.22 + offset, "y": 0.66},
        "right_wrist_basic": {"x": 0.78 + offset, "y": 0.66},
        "left_hip": {"x": 0.42 + offset, "y": 0.72},
        "right_hip": {"x": 0.58 + offset, "y": 0.72},
    }


@pytest.fixture
def sample_frame():
    return build_sample_frame
