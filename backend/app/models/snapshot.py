from sqlalchemy import Column, Integer, Float, ForeignKey
from db.db_manager import Base

class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(Float, nullable=False)

    overall_score = Column(Float, nullable=False)

    focus = Column(Float, nullable=True)
    vitality = Column(Float, nullable=True)
    posture = Column(Float, nullable=True)
    presence = Column(Float, nullable=True)
    composure = Column(Float, nullable=True)
    delivery = Column(Float, nullable=True)

