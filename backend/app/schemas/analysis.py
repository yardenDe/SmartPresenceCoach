from typing import TypeAlias

from pydantic import BaseModel


AnalysisScores: TypeAlias = dict[str, float]


class AnalysisResponse(BaseModel):
    id: int
    timestamp: float
    frames_analyzed: int
    overall_score: float
    scores: AnalysisScores
