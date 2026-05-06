from pydantic import BaseModel


class VerbalMetrics(BaseModel):
    tone_stability: float
    speech_rate: float


class LiveResponse(BaseModel):
    session_id: int
    timestamp: float
    overall_score: float
    
    focus: float
    vitality: float
    posture: float
    presence: float
    composure: float
    
    delivery: VerbalMetrics | None = None
