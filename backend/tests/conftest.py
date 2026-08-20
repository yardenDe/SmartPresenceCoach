"""Shared test configuration and fixtures for backend unit tests."""

from __future__ import annotations

import os
import sys
import types
from enum import Enum
from pathlib import Path

import pytest


PROJECT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_DIR / "app"

# In the Docker image, application modules are copied directly to /app.
if not APP_DIR.exists():
    APP_DIR = PROJECT_DIR

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

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

sys.modules.setdefault("mediapipe", mediapipe_module)
sys.modules.setdefault("mediapipe.tasks", tasks_module)
sys.modules.setdefault("mediapipe.tasks.python", python_module)
sys.modules.setdefault("mediapipe.tasks.python.vision", vision_module)
sys.modules["vision.mediapipe_detector"] = types.SimpleNamespace(
    MediaPipeDetector=DummyMediaPipeDetector
)


def build_sample_frame(offset: float = 0.0) -> dict:
    return {
        "pose": {
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
        },
        "face": {
            "left_iris_center": {"x": 0.46 + offset, "y": 0.24},
            "right_iris_center": {"x": 0.54 + offset, "y": 0.24},
            "left_eye_outer": {"x": 0.44 + offset, "y": 0.24},
            "left_eye_inner": {"x": 0.48 + offset, "y": 0.24},
            "right_eye_inner": {"x": 0.52 + offset, "y": 0.24},
            "right_eye_outer": {"x": 0.56 + offset, "y": 0.24},
            "mouth_top": {"x": 0.50 + offset, "y": 0.34},
            "mouth_bottom": {"x": 0.50 + offset, "y": 0.37 + offset},
            "forehead": {"x": 0.50 + offset, "y": 0.14},
            "chin": {"x": 0.50 + offset, "y": 0.43},
            "left_cheek": {"x": 0.40 + offset, "y": 0.29},
            "right_cheek": {"x": 0.60 + offset, "y": 0.29},
        },
        "hands": [
            {
                "label": "Left",
                "points": {
                    "hand_wrist": {"x": 0.32 + offset, "y": 0.65},
                    "hand_thumb_tip": {"x": 0.29 + offset, "y": 0.58},
                    "hand_index_tip": {"x": 0.30 + offset, "y": 0.55},
                    "hand_middle_tip": {"x": 0.31 + offset, "y": 0.54},
                    "hand_ring_tip": {"x": 0.32 + offset, "y": 0.55},
                    "hand_pinky_tip": {"x": 0.33 + offset, "y": 0.57},
                },
            },
            {
                "label": "Right",
                "points": {
                    "hand_wrist": {"x": 0.68 + offset, "y": 0.65},
                    "hand_thumb_tip": {"x": 0.71 + offset, "y": 0.58},
                    "hand_index_tip": {"x": 0.70 + offset, "y": 0.55},
                    "hand_middle_tip": {"x": 0.69 + offset, "y": 0.54},
                    "hand_ring_tip": {"x": 0.68 + offset, "y": 0.55},
                    "hand_pinky_tip": {"x": 0.67 + offset, "y": 0.57},
                },
            },
        ],
    }


@pytest.fixture
def sample_frame():
    return build_sample_frame
