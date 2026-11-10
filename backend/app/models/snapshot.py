from dataclasses import dataclass


@dataclass
class Snapshot:
    session_id: int
    timestamp: float
    face_direction: float | None = None
    movement_amount: float | None = None
    movement_variation: float | None = None
    head_movement: float | None = None
    shoulder_tilt: float | None = None
    hand_movement: float | None = None
    transcript: str | None = None
    pause_ratio: float | None = None
    average_volume: float | None = None
    volume_variation: float | None = None
    pitch_variation: float | None = None
    id: int | None = None
    end_time: float | None = None
