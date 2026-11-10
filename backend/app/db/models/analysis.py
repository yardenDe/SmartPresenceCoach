from sqlalchemy import Column, Float, ForeignKey, Integer, Text, JSON

from db.db_manager import Base
from media.config import SAMPLE_RATE


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


class AudioFeatureRecord(Base):
    __tablename__ = "audio_features"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    hop_length = Column(Integer, nullable=False)
    sample_rate = Column(Integer, nullable=False, default=SAMPLE_RATE)
    rms = Column(JSON, nullable=False)
    pitch = Column(JSON, nullable=False)
    non_silent_intervals = Column(JSON, nullable=False)
    total_samples = Column(Integer, nullable=False)



# DB records used by Live, Offline and reporting.
AnalysisRecord = VideoMetric | AudioMetric | AudioFeatureRecord | Transcript
