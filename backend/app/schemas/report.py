from datetime import datetime

from pydantic import BaseModel


class ReportRespone(BaseModel):
    session_id: int
    overall_score: float
    summary: str
    recommendations: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class ReportLLMResponse(BaseModel):
    summary: str
    recommendations: str
