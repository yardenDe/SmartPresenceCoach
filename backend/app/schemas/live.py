from pydantic import BaseModel
from typing import Optional

class BodyMetrics(BaseModel):
    posture_stability: float
    shoulder_alignment: float

class HandMetrics(BaseModel):
    hand_gestures: float
    hands_location: float

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

class FrameMetrics(BaseModel):
    body: Optional[BodyMetrics] = None
    face: Optional[FaceMetrics] = None
    hands: Optional[HandMetrics] = None 


class LiveResponse(BaseModel):
    session_id: int
    overall_score: float
    body: Optional[BodyMetrics] = None
    face: Optional[FaceMetrics] = None
    hands: Optional[HandMetrics] = None 
    verbal: Optional[VerbalMetrics] = None


class SkillMetric(BaseModel):
    score: float
    quality: str  
    is_active: bool

class ComprehensiveLiveResponse(BaseModel):
    session_id: int
    overall_score: float
    
    focus: SkillMetric      # Looking at target
    vitality: SkillMetric   # Energy and expression
    posture: SkillMetric    # Body alignment
    presence: SkillMetric   # Spatial confidence
    composure: SkillMetric  # Calmness and stability
    
    delivery: Optional[VerbalMetrics] = None