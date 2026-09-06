from pydantic import BaseModel

from schemas.analysis import Scores


class LiveResponse(BaseModel):
    session_id: int
    timestamp: float
    scores: Scores
