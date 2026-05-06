from pydantic import BaseModel


class AnalysisScores(BaseModel):
    focus: float
    vitality: float
    posture: float
    presence: float
    composure: float
    overall: float


class AnalysisResponse(BaseModel):
    id: int
    timestamp: float
    frames_analyzed: int
    overall_score: float
    scores: AnalysisScores
