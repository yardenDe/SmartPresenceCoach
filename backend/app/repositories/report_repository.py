from sqlalchemy import desc, select
from sqlalchemy.orm import Session as DBSession

from core.exceptions import DatabaseError
from core.logger import get_logger
from models.report import Report
from models.session import Session

logger = get_logger("app.repositories.report")


class ReportRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create_report(
        self,
        session_id: int,
        overall_score: float,
        summary: str,
        recommendations: str,
    ) -> Report:
        report = Report(
            session_id=session_id,
            overall_score=overall_score,
            summary=summary,
            recommendations=recommendations,
        )

        try:
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
        except Exception:
            self.db.rollback()
            logger.exception("event=report.create.failed session_id=%s", session_id)
            raise DatabaseError()

        logger.info(
            "event=report.create.done report_id=%s session_id=%s",
            report.id,
            session_id,
        )
        return report

    def get_by_session(self, session_id: int) -> Report | None:
        try:
            result = self.db.execute(
                select(Report).where(Report.session_id == session_id)
            )
            report = result.scalar_one_or_none()
        except Exception:
            logger.exception("event=report.lookup.failed session_id=%s", session_id)
            raise DatabaseError()

        logger.debug(
            "event=report.lookup.done session_id=%s found=%s",
            session_id,
            report is not None,
        )
        return report

    def list_recent_by_user(self, user_id: int, limit: int = 5) -> list[tuple[Report, Session]]:
        try:
            result = self.db.execute(
                select(Report, Session)
                .join(Session, Session.id == Report.session_id)
                .where(Session.user_id == user_id)
                .order_by(desc(Report.generated_at), desc(Report.id))
                .limit(limit)
            )
        except Exception:
            logger.exception("event=report.recent.failed user_id=%s", user_id)
            raise DatabaseError()

        rows = [(report, session) for report, session in result.all()]
        logger.debug("event=report.recent.done user_id=%s count=%s", user_id, len(rows))
        return rows
