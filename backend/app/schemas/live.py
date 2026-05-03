from fastapi import File, Form, UploadFile
from pydantic import BaseModel


class VerbalMetrics(BaseModel):
    tone_stability: float
    speech_rate: float


class LiveRequest(BaseModel):
    session_id: int
    timestamp: float
    frame_data: str
    video: UploadFile


class LiveResponse(BaseModel):
    session_id: int
    overall_score: float
    
    focus: float
    vitality: float
    posture: float
    presence: float
    composure: float
    
    delivery: VerbalMetrics | None = None
