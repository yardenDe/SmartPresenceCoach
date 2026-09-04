from pydantic import BaseModel


class VisualAnalysis(BaseModel):
    focus: float | None = None
    posture: float | None = None
    engagement: float | None = None
    presence: float | None = None
    composure: float | None = None
    overall: float


class AudioAnalysis(BaseModel):
    volume: float | None = None
    pitch_variation: float | None = None
    speaking_pace: float | None = None
    pause_ratio: float | None = None
    overall: float
