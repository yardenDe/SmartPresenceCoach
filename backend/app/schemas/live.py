from pydantic import BaseModel

from schemas.analysis import Analysis


class LiveResponse(BaseModel):
    session_id: int
    timestamp: float
    analysis: Analysis
