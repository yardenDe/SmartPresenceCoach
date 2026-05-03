from datetime import datetime

from pydantic import BaseModel


class ReportRead(BaseModel):
    session_id: int
    score: float
    summary: str
    recommendations: str
    generated_at: datetime
