from pydantic import BaseModel

from schemas.analysis import AnalysisResponse


class OfflineResponse(BaseModel):
    session_id: int
    overall_score: float
    results: list[AnalysisResponse]
