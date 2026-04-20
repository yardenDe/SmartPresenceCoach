from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.sql import func
from db.db_manager import Base

class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    timestamp_seconds = Column(Float, nullable=False)

    overall_score = Column(Float, nullable=False)

    posture_stability = Column(Float, nullable=True)
    shoulder_alignment = Column(Float, nullable=True)
    hand_gestures = Column(Float, nullable=True)

    eye_contact = Column(Float, nullable=True)
    facial_energy = Column(Float, nullable=True)
    head_tilt = Column(Float, nullable=True)

    tone_stability = Column(Float, nullable=True)
    speech_rate = Column(Float, nullable=True)
