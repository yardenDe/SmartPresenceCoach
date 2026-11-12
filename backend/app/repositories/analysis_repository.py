from sqlalchemy import select, delete
from sqlalchemy.orm import Session as DBSession

from core.exceptions import DatabaseError
from core.logger import get_logger
from db.models.analysis import AnalysisRecord, AudioFeatureRecord, AudioMetric, Transcript, VideoMetric

logger = get_logger("app.repositories.snapshot")


class AnalysisRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create_records(self, records: list[AnalysisRecord]) -> None:
        if not records:
            return

        try:
            logger.debug("event=analysis.bulk_create.start count=%s", len(records))
            self.db.add_all(records)
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.exception("event=analysis.bulk_create.failed count=%s", len(records))
            raise DatabaseError()

        logger.info("event=analysis.bulk_create.done count=%s", len(records))

    def replace_transcripts(self, session_id: int, records: list[Transcript]) -> None:
        logger.debug("event=transcript.replace.start session_id=%s count=%s", session_id, len(records))
        try:
            self.db.execute(delete(Transcript).where(Transcript.session_id == session_id))
            self.db.add_all(records)
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.exception("event=transcript.replace.failed session_id=%s", session_id)
            raise DatabaseError()
        logger.info("event=transcript.replace.done session_id=%s count=%s", session_id, len(records))

    def get_by_session(self, session_id: int) -> list[AnalysisRecord]:
        logger.debug("event=analysis.get_by_session.start session_id=%s", session_id)
        try:
            records = []

            for model in (VideoMetric, AudioMetric, Transcript, AudioFeatureRecord):
                query = (
                    select(model)
                    .where(model.session_id == session_id)
                    .order_by(model.start_time, model.id)
                )
                rows = self.db.scalars(query).all()
                logger.debug(
                    "event=analysis.get_by_session.loaded session_id=%s model=%s count=%s",
                    session_id, model.__name__, len(rows),
                )
                records.extend(rows)

            logger.debug("event=analysis.get_by_session.done session_id=%s count=%s", session_id, len(records))
            return records

        except Exception:
            logger.exception("event=snapshot.get_by_session.failed session_id=%s", session_id)
            raise DatabaseError()
