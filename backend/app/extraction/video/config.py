from dataclasses import dataclass


@dataclass
class Landmark:
    x: float
    y: float
    z: float | None = None


@dataclass
class FrameLandmarks:
    nose: Landmark | None = None
    left_eye_inner: Landmark | None = None
    right_eye_inner: Landmark | None = None
    left_ear: Landmark | None = None
    right_ear: Landmark | None = None
    left_shoulder: Landmark | None = None
    right_shoulder: Landmark | None = None
    left_elbow: Landmark | None = None
    right_elbow: Landmark | None = None
    left_wrist: Landmark | None = None
    right_wrist: Landmark | None = None
    left_hip: Landmark | None = None
    right_hip: Landmark | None = None
    left_knee: Landmark | None = None
    right_knee: Landmark | None = None
    left_ankle: Landmark | None = None
    right_ankle: Landmark | None = None