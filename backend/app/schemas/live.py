from pydantic import BaseModel

from analytics.config import Scores


class LiveResponse(BaseModel):
    session_id: int
    timestamp: float
    scores: Scores
