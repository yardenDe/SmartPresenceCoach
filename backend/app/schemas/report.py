from datetime import datetime

from pydantic import BaseModel


class ReportRead(BaseModel):
    session_id: int
    overall_score: float
    summary: str
    recommendations: str
    generated_at: datetime
