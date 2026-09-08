from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from core.exceptions import DatabaseError
from core.logger import get_logger
from models.snapshot import Snapshot

logger = get_logger("app.repositories.snapshot")


class SnapshotRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create_snapshots(
        self,
        snapshots: list[Snapshot],
    ) -> list[Snapshot]:
        if not snapshots:
            return []

        try:
            self.db.add_all(snapshots)
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.exception(
                "event=snapshot.bulk_create.failed count=%s",
                len(snapshots),
            )
            raise DatabaseError()

        logger.info(
            "event=snapshot.bulk_create.done count=%s",
            len(snapshots),
        )

        return snapshots


    def get_by_session(
        self,
        session_id: int,
    ) -> list[Snapshot]:
        try:
            query = (
                select(Snapshot)
                .where(Snapshot.session_id == session_id)
                .order_by(
                    Snapshot.timestamp.asc(),
                    Snapshot.id.asc(),
                )
            )

            return self.db.execute(query).scalars().all()

        except Exception:
            logger.exception(
                "event=snapshot.get_by_session.failed session_id=%s",
                session_id,
            )
            raise DatabaseError()
