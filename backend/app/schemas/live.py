from pydantic import BaseModel

from schemas.analysis import VisualAnalysis


class LiveResponse(BaseModel):
    session_id: int
    timestamp: float
    analysis: VisualAnalysis
