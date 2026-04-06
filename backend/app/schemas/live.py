from pydantic import BaseModel
from typing import Optional

class BodyMetrics(BaseModel):
    posture_stability: float
    shoulder_alignment: float
    hand_gestures: float

class FaceMetrics(BaseModel):
    eye_contact: float
    facial_energy: float
    head_tilt: float

class VerbalMetrics(BaseModel):
    tone_stability: float
    speech_rate: float

class FrameRequest(BaseModel):
    session_id: int
    timestamp: float
    frame_data: str 

class LiveResponse(BaseModel):
    session_id: int
    overall_score: float
    body: Optional[BodyMetrics] = None
    face: Optional[FaceMetrics] = None
    verbal: Optional[VerbalMetrics] = None
    
