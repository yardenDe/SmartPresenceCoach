from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, Text
from sqlalchemy.sql import func
from db.db_manager import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), unique=True, nullable=False)
    overall_score = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=False)
    report_data = Column(JSON, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
