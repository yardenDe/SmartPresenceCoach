from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from analytics.timeline_builder import TimelineBuilder, TimelineEntry
from core.exceptions import DatabaseError
from core.logger import get_logger
from models.analysis_data import AudioMetric, Transcript, VideoMetric
from models.snapshot import Snapshot

logger = get_logger("app.repositories.snapshot")
RECORD_FIELDS = (
    (VideoMetric, (
        "face_direction", "movement_amount", "movement_variation",
        "head_movement", "shoulder_tilt", "hand_movement",
    )),
    (AudioMetric, (
        "pause_ratio", "average_volume", "volume_variation", "pitch_variation",
    )),
    (Transcript, ("transcript",)),
)


class SnapshotRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create_snapshots(self, snapshots: list[Snapshot]) -> list[Snapshot]:
        records = []
        for snapshot in snapshots:
            for model, fields in RECORD_FIELDS:
                values = {name: getattr(snapshot, name) for name in fields}
                if any(value is not None for value in values.values()):
                    records.append(model(
                        session_id=snapshot.session_id,
                        start_time=snapshot.timestamp,
                        end_time=snapshot.end_time if snapshot.end_time is not None else snapshot.timestamp,
                        **values,
                    ))
        self.create_records(records)
        return snapshots

    def create_records(self, records: list[VideoMetric | AudioMetric | Transcript]) -> None:
        if not records:
            return

        try:
            self.db.add_all(records)
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.exception("event=analysis.bulk_create.failed count=%s", len(records))
            raise DatabaseError()

        logger.info("event=analysis.bulk_create.done count=%s", len(records))

    def get_by_session(self, session_id: int) -> list[Snapshot]:
        try:
            streams = []
            for model, fields in RECORD_FIELDS:
                query = (
                    select(model.start_time, model.end_time, *(getattr(model, name) for name in fields))
                    .where(model.session_id == session_id)
                    .order_by(model.start_time, model.id)
                )
                streams.append([
                    TimelineEntry(row.start_time, row.end_time, {name: row[name] for name in fields})
                    for row in self.db.execute(query).mappings()
                ])
            return TimelineBuilder().build(session_id, streams)
        except Exception:
            logger.exception("event=snapshot.get_by_session.failed session_id=%s", session_id)
            raise DatabaseError()
