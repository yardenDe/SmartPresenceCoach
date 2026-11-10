from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict


ANALYSIS_WINDOW_SECONDS = 3.0

MIN_SCORE = 0.0
MAX_SCORE = 100.0


class MetricDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    unit: str
    min_value: float
    max_value: float
    target_min: float
    target_max: float


METRIC_DEFINITIONS = {
    "face_direction": MetricDefinition(
        unit="deg",
        min_value=0.0, max_value=90.0, target_min=0.0, target_max=15.0,
    ),
    "movement_amount": MetricDefinition(
        unit="body-scale/sec",
        min_value=0.0, max_value=2.0, target_min=0.10, target_max=0.60,
    ),
    "movement_variation": MetricDefinition(
        unit="body-scale/sec",
        min_value=0.0, max_value=1.0, target_min=0.0, target_max=0.15,
    ),
    "head_movement": MetricDefinition(
        unit="deg/sec",
        min_value=0.0, max_value=180.0, target_min=3.0, target_max=30.0,
    ),
    "shoulder_tilt": MetricDefinition(
        unit="deg",
        min_value=0.0, max_value=90.0, target_min=0.0, target_max=8.0,
    ),
    "hand_movement": MetricDefinition(
        unit="body-scale/sec",
        min_value=0.0, max_value=3.0, target_min=0.10, target_max=0.80,
    ),
    "pause_ratio": MetricDefinition(
        unit="ratio",
        min_value=0.0, max_value=1.0, target_min=0.10, target_max=0.35,
    ),
    "average_volume": MetricDefinition(
        unit="dBFS",
        min_value=-60.0, max_value=0.0, target_min=-30.0, target_max=-12.0,
    ),
    "volume_variation": MetricDefinition(
        unit="dB",
        min_value=0.0, max_value=30.0, target_min=3.0, target_max=10.0,
    ),
    "pitch_variation": MetricDefinition(
        unit="semitones",
        min_value=0.0, max_value=12.0, target_min=1.5, target_max=5.0,
    ),
}


class VideoMetrics(BaseModel):
    face_direction: float | None = None
    movement_amount: float | None = None
    movement_variation: float | None = None
    head_movement: float | None = None
    shoulder_tilt: float | None = None
    hand_movement: float | None = None


class AudioMetrics(BaseModel):
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


@dataclass
class Snapshot:
    session_id: int
    start_time: float
    end_time: float
    video: VideoMetrics | None = None
    audio: AudioMetrics | None = None
    transcript: str | None = None
