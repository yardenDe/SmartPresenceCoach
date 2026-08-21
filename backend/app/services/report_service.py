from core.exceptions import LLMUnavailableError, SessionNotFoundError, SnapshotsNotFoundError, UnauthorizedError
from core.logger import get_logger
from llm.prompts import session_report_prompt, session_report_system_instruction
from models.session import Session as SessionModel
from repositories.report_repository import ReportRepository
from repositories.session_repository import SessionRepository
from repositories.snapshot_repository import SnapshotRepository
from schemas.report import FullReportResponse, LLMReportText, ShortReportResponse
from services.llm_service import LLMService


class ReportService:
    METRICS = ["focus", "posture", "presence", "engagement", "composure"]

    def __init__(
        self,
        session_repository: SessionRepository,
        snapshot_repository: SnapshotRepository,
        report_repository: ReportRepository,
    ):
        self.session_repository = session_repository
        self.snapshot_repository = snapshot_repository
        self.report_repository = report_repository
        self.logger = get_logger("app.reports")

    def generate_short_report(self, user_id: int, session_id: int) -> ShortReportResponse:
        self._validate_session(user_id, session_id)

        rows = self.snapshot_repository.get_metrics_timeline(["overall"], session_id)
        if not rows:
            raise SnapshotsNotFoundError()

        metrics_states = self._get_metrics_stats(session_id)
        timeline_data = self._build_timeline(rows, ["overall"])

        report = {
            "session_id": session_id,
            "overall_score": metrics_states["overall_avg"],
            "overall_state": self._build_overall_state(metrics_states, timeline_data["series"]["overall"]),
            "timeline": timeline_data,
            "metrics": self._build_metrics_summary(metrics_states),
        }
        return ShortReportResponse.model_validate(report)

    def list_recent_reports(self, user_id: int, limit: int = 5) -> list[dict]:
        return [
            {
                "session_id": session.id,
                "mode": session.mode,
                "started_at": session.start_time,
                "ended_at": session.end_time,
                "overall_score": report.overall_score,
                "generated_at": report.generated_at,
            }
            for report, session in self.report_repository.list_recent_by_user(
                user_id=user_id,
                limit=limit,
            )
        ]

    def generate_full_report(
        self,
        user_id: int,
        session_id: int,
        llm_service: LLMService | None = None,
    ) -> FullReportResponse:
        session = self._validate_session(user_id, session_id)

        existing_report = self.report_repository.get_by_session(session_id)
        if existing_report and existing_report.report_data:
            return FullReportResponse.model_validate(existing_report.report_data)

        all_metrics = ["overall"] + self.METRICS
        rows = self.snapshot_repository.get_metrics_timeline(all_metrics, session_id)
        if not rows:
            raise SnapshotsNotFoundError()

        metrics_states = self._get_metrics_stats(session_id)
        timeline_data = self._build_timeline(rows, all_metrics)

        report = {
            "session_id": session_id,
            "overall_score": metrics_states["overall_avg"],
            "overall_state": self._build_overall_state(metrics_states, timeline_data["series"]["overall"]),
            "timeline": timeline_data,
            "metrics": self._build_metrics_summary(metrics_states),
            **self._build_llm_report_text(
                overall_score=metrics_states["overall_avg"],
                timeline_data=timeline_data,
                mode=session.mode,
                llm_service=llm_service,
            ),
        }
        self._create_full_report(session_id, report)

        return FullReportResponse.model_validate(report)

    def _validate_session(self, user_id: int, session_id: int) -> SessionModel:
        session = self.session_repository.get_by_id(session_id)
        if not session:
            self.logger.warning("event=report.session_missing session_id=%s user_id=%s", session_id, user_id)
            raise SessionNotFoundError()

        if session.user_id != user_id:
            self.logger.warning(
                "event=report.session_denied session_id=%s user_id=%s owner_id=%s",
                session_id,
                user_id,
                session.user_id,
            )
            raise UnauthorizedError()

        return session

    def _create_full_report(self, session_id: int, report: dict) -> None:
        self.report_repository.create_report(
            session_id=session_id,
            overall_score=report["overall_score"],
            summary=report["summary"],
            recommendations=report["recommendations"],
            report_data=report,
        )

    def _build_llm_report_text(
        self,
        overall_score: float,
        timeline_data: dict,
        mode: str | None,
        llm_service: LLMService | None,
    ) -> dict:
        if llm_service is None:
            return self._fallback_report_text()

        prompt = session_report_prompt(
            overall_score=overall_score,
            timestamps=timeline_data["timestampsSec"],
            metric_vectors=timeline_data["series"],
            mode=mode,
        )

        try:
            text = llm_service.generate_json(
                prompt,
                LLMReportText,
                system_instruction=session_report_system_instruction(),
            )
            return text.model_dump()
        except LLMUnavailableError:
            self.logger.warning("event=report.llm_unavailable fallback=true")
            return self._fallback_report_text()

    def _fallback_report_text(self) -> dict:
        return {
            "summary": "Your metric timeline was generated successfully, but the AI coaching summary is temporarily unavailable.",
            "recommendations": "Review the detailed charts, focus on your lowest average metric, and repeat the session later to generate the AI coaching text.",
        }

    def _get_metrics_stats(self, session_id: int) -> dict:
        all_metrics = ["overall"] + self.METRICS
        stats = self.snapshot_repository.get_metrics_stats(all_metrics, session_id)
        if not stats or stats.get("overall_avg") is None:
            raise SnapshotsNotFoundError()
        return stats

    def _build_overall_state(self, stats: dict, overall_scores: list[float]) -> dict:
        return {
            "avg": stats["overall_avg"],
            "min": stats["overall_min"],
            "max": stats["overall_max"],
            "trend": self._trend(overall_scores),
        }

    def _build_metrics_summary(self, stats: dict) -> dict:
        return {
            metric: {
                "avg": stats[f"{metric}_avg"],
                "min": stats[f"{metric}_min"],
                "max": stats[f"{metric}_max"],
            }
            for metric in self.METRICS
        }

    def _build_timeline(self, rows: list, metrics: list[str]) -> dict:
        return {
            "timestampsSec": [float(row["timestamp"]) for row in rows],
            "series": {
                metric: [float(row[metric]) if row[metric] is not None else None for row in rows]
                for metric in metrics
            },
        }

    def _trend(self, values: list[float]) -> str:
        if len(values) < 2:
            return "stable"

        delta = values[-1] - values[0]
        if delta > 2:
            return "up"
        if delta < -2:
            return "down"
        return "stable"