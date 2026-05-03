from pydantic import BaseModel


class AnalysisScores(BaseModel):
    focus: float
    posture: float
    vitality: float
    presence: float
    composure: float
    overall: float


class AnalysisChunk(BaseModel):
    chunk_id: int
    scores: AnalysisScores
