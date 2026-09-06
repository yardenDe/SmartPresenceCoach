import numpy as np
from pydantic import BaseModel, ConfigDict


class VisualMetrics(BaseModel):
    gaze_direction: float | None = None
    movement_amount: float | None = None
    movement_variation: float | None = None
    head_movement: float | None = None
    shoulder_tilt: float | None = None
    hand_movement: float | None = None


class AudioMetrics(BaseModel):
    transcript: str | None = None
    pause_ratio: float | None = None
    average_volume: float | None = None
    volume_variation: float | None = None
    pitch_variation: float | None = None


class Scores(BaseModel):
    focus: float | None = None
    posture: float | None = None
    engagement: float | None = None
    presence: float | None = None
    composure: float | None = None
    overall: float | None = None


class AudioFeatures(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    rms: np.ndarray
    pitch: np.ndarray
    non_silent_intervals: np.ndarray
    total_samples: int
    transcript: str | None = None


class Analysis(BaseModel):
    visual: VisualMetrics | None = None
    audio: AudioMetrics | None = None
