from sqlalchemy import Column, Float, ForeignKey, Integer, Text
from db.db_manager import Base

class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(Float, nullable=False)

    gaze_direction = Column(Float, nullable=True)
    movement_amount = Column(Float, nullable=True)
    movement_variation = Column(Float, nullable=True)
    head_movement = Column(Float, nullable=True)
    shoulder_tilt = Column(Float, nullable=True)
    hand_movement = Column(Float, nullable=True)

    transcript = Column(Text, nullable=True)
    pause_ratio = Column(Float, nullable=True)
    average_volume = Column(Float, nullable=True)
    volume_variation = Column(Float, nullable=True)
    pitch_variation = Column(Float, nullable=True)

