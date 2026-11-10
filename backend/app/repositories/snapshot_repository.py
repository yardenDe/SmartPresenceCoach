from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from core.exceptions import DatabaseError
from core.logger import get_logger
from db.models.analysis import AudioFeatureRecord, AudioMetric, Transcript, VideoMetric

logger = get_logger("app.repositories.snapshot")


class SnapshotRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create_records(self, records: list[VideoMetric | AudioMetric | AudioFeatureRecord | Transcript]) -> None:
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

    def get_by_session(self, session_id: int) -> list[VideoMetric | AudioMetric | AudioFeatureRecord | Transcript]:
        try:
            records = []

            for model in (VideoMetric, AudioMetric, Transcript, AudioFeatureRecord):
                query = (
                    select(model)
                    .where(model.session_id == session_id)
                    .order_by(model.start_time, model.id)
                )
                records.extend(self.db.scalars(query).all())

            return records

        except Exception:
            logger.exception("event=snapshot.get_by_session.failed session_id=%s", session_id)
            raise DatabaseError()
