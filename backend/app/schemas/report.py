from pydantic import BaseModel
from datetime import datetime

class Report(BaseModel):
    session_id: int
    score: float
    summary: str
    recommendations: str
    generated_at: datetime 