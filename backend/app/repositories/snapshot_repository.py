from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DBSession

from core.exceptions import DatabaseError
from core.logger import get_logger
from models.snapshot import Snapshot

logger = get_logger("app.repositories.snapshot")


class SnapshotRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create_snapshot(
        self,
        session_id: int,
        timestamp: float,
        scores: dict[str, Any],
    ) -> Snapshot:
        snapshot = Snapshot(
            session_id=session_id,
            timestamp=timestamp,
            overall_score=float(scores.get("overall_score", scores.get("overall", 0.0))),
            focus=float(scores.get("focus", 0.0)),
            vitality=float(scores.get("vitality", 0.0)),
            posture=float(scores.get("posture", 0.0)),
            presence=float(scores.get("presence", 0.0)),
            composure=float(scores.get("composure", 0.0)),
            delivery=float(scores.get("delivery", 0.0)),
        )

        try:
            self.db.add(snapshot)
            self.db.commit()
            self.db.refresh(snapshot)
        except Exception:
            self.db.rollback()
            logger.exception("event=snapshot.create.failed session_id=%s", session_id)
            raise DatabaseError()

        logger.info(
            "event=snapshot.create.done snapshot_id=%s session_id=%s",
            snapshot.id,
            session_id,
        )
        return snapshot

    def get_by_id(self, snapshot_id: int) -> Snapshot | None:
        try:
            snapshot = self.db.get(Snapshot, snapshot_id)
        except Exception:
            logger.exception("event=snapshot.lookup.failed snapshot_id=%s", snapshot_id)
            raise DatabaseError()

        logger.debug(
            "event=snapshot.lookup.done snapshot_id=%s found=%s",
            snapshot_id,
            snapshot is not None,
        )
        return snapshot

    def list_by_session(self, session_id: int) -> list[Snapshot]:
        try:
            result = self.db.execute(
                select(Snapshot)
                .where(Snapshot.session_id == session_id)
                .order_by(Snapshot.timestamp.asc(), Snapshot.id.asc())
            )
            snapshots = list(result.scalars().all())
        except Exception:
            logger.exception("event=snapshot.list.failed session_id=%s", session_id)
            raise DatabaseError()

        logger.debug(
            "event=snapshot.list.done session_id=%s count=%s",
            session_id,
            len(snapshots),
        )
        return snapshots

    def delete_by_session(self, session_id: int) -> int:
        try:
            result = self.db.execute(delete(Snapshot).where(Snapshot.session_id == session_id))
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.exception("event=snapshot.delete.failed session_id=%s", session_id)
            raise DatabaseError()

        deleted_count = result.rowcount or 0
        logger.info(
            "event=snapshot.delete.done session_id=%s count=%s",
            session_id,
            deleted_count,
        )
        return deleted_count
