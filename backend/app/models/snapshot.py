from sqlalchemy import Column, Float, ForeignKey, Integer, Text
from db.db_manager import Base

class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(Float, nullable=False)

    overall = Column(Float, nullable=False)

    focus = Column(Float, nullable=True)
    engagement = Column(Float, nullable=True)
    posture = Column(Float, nullable=True)
    presence = Column(Float, nullable=True)
    composure = Column(Float, nullable=True)
    
    delivery = Column(Float, nullable=True)

    transcript = Column(Text, nullable=True)
    pause_ratio = Column(Float, nullable=True)
    average_volume = Column(Float, nullable=True)
    volume_variation = Column(Float, nullable=True)
    pitch_variation = Column(Float, nullable=True)

