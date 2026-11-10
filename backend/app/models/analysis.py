from sqlalchemy import Column, Float, ForeignKey, Integer, Text

from db.db_manager import Base


class VideoMetric(Base):
    __tablename__ = "video_metrics"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)

    face_direction = Column(Float)
    movement_amount = Column(Float)
    movement_variation = Column(Float)
    head_movement = Column(Float)
    shoulder_tilt = Column(Float)
    hand_movement = Column(Float)


class AudioMetric(Base):
    __tablename__ = "audio_metrics"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)

    pause_ratio = Column(Float)
    average_volume = Column(Float)
    volume_variation = Column(Float)
    pitch_variation = Column(Float)


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)

    transcript = Column(Text, nullable=False)
