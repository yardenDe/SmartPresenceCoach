from typing import Any
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DBSession

from core.exceptions import DatabaseError
from core.logger import get_logger
from models.snapshot import Snapshot
from schemas.analysis import Analysis

logger = get_logger("app.repositories.snapshot")


class SnapshotRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create_snapshots(
        self,
        session_id: int,
        snapshots: list[dict[str, Any]],
    ) -> list[Snapshot]:
        if not snapshots:
            return []

<<<<<<< Updated upstream
        snapshot_models = [
            Snapshot(
                session_id=session_id,
                timestamp=snapshot.get("timestamp"),
                overall=snapshot["overall"],
                focus=snapshot.get("focus"),
                engagement=snapshot.get("engagement"),
                posture=snapshot.get("posture"),
                presence=snapshot.get("presence"),
                composure=snapshot.get("composure"),
                delivery=snapshot.get("delivery"),
=======
        snapshot_models = []

        for snapshot in snapshots:
            analysis: Analysis = snapshot["analysis"]
            visual = analysis.visual
            audio = analysis.audio

            if visual is None and audio is None:
                continue

            analysis_data = {}

            if visual is not None:
                analysis_data.update(
                    visual.model_dump(exclude_none=True)
                )

            if audio is not None:
                analysis_data.update(
                    audio.model_dump(exclude_none=True)
                )

            snapshot_models.append(
                Snapshot(
                    session_id=session_id,
                    timestamp=snapshot["timestamp"],
                    **analysis_data,
                )
>>>>>>> Stashed changes
            )

        if not snapshot_models:
            return []

        try:
            self.db.add_all(snapshot_models)
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.exception(
                "event=snapshot.bulk_create.failed session_id=%s",
                session_id,
            )
            raise DatabaseError()

        logger.info(
            "event=snapshot.bulk_create.done session_id=%s count=%s",
            session_id,
            len(snapshot_models),
        )
        return snapshot_models

    def get_by_id(self, snapshot_id: int) -> Snapshot | None:
        try:
            snapshot = self.db.get(Snapshot, snapshot_id)
        except Exception:
            logger.exception(
                "event=snapshot.lookup.failed snapshot_id=%s",
                snapshot_id,
            )
            raise DatabaseError()

        logger.debug(
            "event=snapshot.lookup.done snapshot_id=%s found=%s",
            snapshot_id,
            snapshot is not None,
        )
        return snapshot

    def list_by_session(self, session_id: int) -> list[Snapshot]:
        try:
            query = (
                select(Snapshot)
                .where(Snapshot.session_id == session_id)
                .order_by(Snapshot.timestamp.asc(), Snapshot.id.asc())
            )
            result = self.db.execute(query)
            snapshots = result.scalars().all()
        except Exception:
            logger.exception(
                "event=snapshot.list.failed session_id=%s",
                session_id,
            )
            raise DatabaseError()

        logger.debug(
            "event=snapshot.list.done session_id=%s count=%s",
            session_id,
            len(snapshots),
        )
        return snapshots

    def get_metric_values(
        self,
        metrics: list[str],
        session_id: int,
    ) -> list[dict[str, Any]]:
        columns = [Snapshot.timestamp] + [
            getattr(Snapshot, metric)
            for metric in metrics
        ]

        try:
            query = (
                select(*columns)
                .where(Snapshot.session_id == session_id)
                .order_by(Snapshot.timestamp.asc(), Snapshot.id.asc())
            )
            result = self.db.execute(query).mappings().all()
        except Exception:
            logger.exception(
                "event=snapshot.metric_values.failed session_id=%s",
                session_id,
            )
            raise DatabaseError()

        logger.debug(
            "event=snapshot.metric_values.done session_id=%s count=%s metrics=%s",
            session_id,
            len(result),
            metrics,
        )
        return result

    def get_metrics_stats(
        self,
        metrics: list[str],
        session_id: int,
    ) -> dict[str, Any]:
        select_fields = []

        for metric in metrics:
            column = getattr(Snapshot, metric)
            select_fields.extend([
                func.avg(column).label(f"{metric}_avg"),
                func.min(column).label(f"{metric}_min"),
                func.max(column).label(f"{metric}_max"),
            ])

        try:
            query = select(*select_fields).where(
                Snapshot.session_id == session_id
            )
            row_map = self.db.execute(query).mappings().one_or_none()
            return dict(row_map) if row_map else {}
        except Exception:
            logger.exception(
                "event=snapshot.all_metrics_stats.failed session_id=%s",
                session_id,
            )
            raise DatabaseError()
