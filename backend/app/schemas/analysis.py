from pydantic import BaseModel


class AnalysisScores(BaseModel):

    focus: float | None = None
    posture: float | None = None
    vitality: float | None = None
    presence: float | None = None
    composure: float | None = None


class AnalysisResponse(BaseModel):
    id: int
    timestamp: float
    frames_analyzed: int
    overall_score: float
    scores: AnalysisScores
