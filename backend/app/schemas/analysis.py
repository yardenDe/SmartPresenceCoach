import numpy as np
from pydantic import BaseModel, ConfigDict


class AnalysisScores(BaseModel):

    focus: float | None = None
    posture: float | None = None
    engagement: float | None = None
    presence: float | None = None
    composure: float | None = None


<<<<<<< Updated upstream
class AnalysisResponse(BaseModel):
    id: int
    timestamp: float
    frames_analyzed: int
    overall: float
    scores: AnalysisScores
=======
class AudioAnalysis(BaseModel):
    transcript: str | None = None
    pause_ratio: float | None = None
    average_volume: float | None = None
    volume_variation: float | None = None
    pitch_variation: float | None = None


class AudioFeatures(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    rms: np.ndarray
    pitch: np.ndarray
    non_silent_intervals: np.ndarray
    total_samples: int
    transcript: str | None = None


class Analysis(BaseModel):
    visual: VisualAnalysis | None = None
    audio: AudioAnalysis | None = None
>>>>>>> Stashed changes
