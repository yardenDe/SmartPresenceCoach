from analytics.config import AUDIO_METRICS, VISUAL_METRICS
from core.exceptions import (
    LLMUnavailableError,
    ReportNotFoundError,
    SnapshotsNotFoundError,
)
from core.logger import get_logger
from llm.prompts import session_report_prompt, session_report_system_instruction
from repositories.report_repository import ReportRepository
from repositories.snapshot_repository import SnapshotRepository
from schemas.report import LLMReportText
from services.llm_service import LLMService
from services.session_service import SessionService

logger = get_logger("app.reports")


class ReportService:
    def __init__(
        self,
        session_service: SessionService,
        snapshot_repository: SnapshotRepository,
        report_repository: ReportRepository,
    ):
        self.session_service = session_service
        self.snapshot_repository = snapshot_repository
        self.report_repository = report_repository

    def generate_report(
        self,
        user_id: int,
        session_id: int,
        fields: set[str],
        llm_service: LLMService | None = None,
    ) -> dict:
        session = self.session_service.require_owned_session(
            user_id,
            session_id,
        )

        metric_names = [
            "overall",
            *VISUAL_METRICS,
            *AUDIO_METRICS,
        ]

        rows = self.snapshot_repository.get_metric_values(
            [*metric_names, "transcript"],
            session_id,
        )
        if not rows:
            raise SnapshotsNotFoundError()

        metric_values = self._align(rows)

        metric_stats = self.snapshot_repository.get_metrics_stats(
            ["overall", *VISUAL_METRICS],
            session_id,
        )
        if not metric_stats or metric_stats.get("overall_avg") is None:
            raise SnapshotsNotFoundError()

        report = {
            "session_id": session_id,
        }

        if "overall_score" in fields:
            report["overall_score"] = metric_stats["overall_avg"]

        if "overall_state" in fields:
            report["overall_state"] = self._summarize_metric(
                metric_stats,
                "overall",
                metric_values["overall"],
            )

        if "metrics" in fields:
            report["metrics"] = {
                metric: self._summarize_metric(metric_stats, metric)
                for metric in VISUAL_METRICS
            }

        if "timeline" in fields:
            report["timeline"] = {
                "timestampsSec": metric_values["timestamp"],
                "series": {
                    metric: metric_values[metric]
                    for metric in metric_names
                },
                "transcripts": metric_values["transcript"],
            }

        if "summary" in fields or "recommendations" in fields:
            llm_content = self._get_llm_content(
                session_id=session_id,
                overall_score=metric_stats["overall_avg"],
                metric_values=metric_values,
                mode=session.mode,
                llm_service=llm_service,
            )

            if "summary" in fields:
                report["summary"] = llm_content["summary"]

            if "recommendations" in fields:
                report["recommendations"] = llm_content["recommendations"]

        return report

    def list_recent_reports(
        self,
        user_id: int,
        limit: int = 5,
    ) -> list[dict]:
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

    def get_full_report_data(
        self,
        user_id: int,
        session_id: int,
    ) -> dict:
        self.session_service.require_owned_session(
            user_id,
            session_id,
        )

        saved_report = self.report_repository.get_by_session(session_id)
        if (
            saved_report is None
            or saved_report.summary is None
            or saved_report.recommendations is None
        ):
            raise ReportNotFoundError()

        return self.generate_report(
            user_id=user_id,
            session_id=session_id,
            fields={
                "overall_score",
                "overall_state",
                "metrics",
                "timeline",
                "summary",
                "recommendations",
            },
        )

    def _summarize_metric(
        self,
        metric_stats: dict,
        metric: str,
        metric_values: list[float] | None = None,
    ) -> dict:
        summary = {
            "avg": metric_stats[f"{metric}_avg"],
            "min": metric_stats[f"{metric}_min"],
            "max": metric_stats[f"{metric}_max"],
        }

        if metric_values is not None:
            summary["trend"] = self._trend(metric_values)

        return summary

    def _get_llm_content(
        self,
        session_id: int,
        overall_score: float,
        metric_values: dict,
        mode: str | None,
        llm_service: LLMService | None,
    ) -> dict:
        saved_report = self.report_repository.get_by_session(session_id)

        if (
            saved_report is not None
            and saved_report.summary is not None
            and saved_report.recommendations is not None
        ):
            return {
                "summary": saved_report.summary,
                "recommendations": saved_report.recommendations,
            }

        fallback_content = {
            "summary": "Your metric timeline was generated successfully, but the AI coaching summary is temporarily unavailable.",
            "recommendations": "Review the detailed charts, focus on your lowest average metric, and repeat the session later to generate the AI coaching text.",
        }

        if llm_service is None:
            return fallback_content

        prompt = session_report_prompt(
            timestamps=metric_values["timestamp"],
            visual_metric_vectors={
                metric: metric_values[metric]
                for metric in ["overall", *VISUAL_METRICS]
            },
            audio_metric_vectors={
                metric: metric_values[metric]
                for metric in AUDIO_METRICS
            },
            transcript_vector=metric_values["transcript"],
            mode=mode,
        )

        try:
            content = llm_service.generate_json(
                prompt,
                LLMReportText,
                system_instruction=session_report_system_instruction(),
            ).model_dump()
        except LLMUnavailableError:
            logger.warning(
                "event=report.llm_unavailable fallback=true"
            )
            return fallback_content

        self.report_repository.create_report(
            session_id=session_id,
            overall_score=overall_score,
            summary=content["summary"],
            recommendations=content["recommendations"],
        )

        return content

    @staticmethod
    def _align(
        rows: list[dict],
    ) -> dict[str, list]:
        return {
            field: [row.get(field) for row in rows]
            for field in rows[0].keys()
        }

    @staticmethod
    def _trend(
        values: list[float],
    ) -> str:
        if len(values) < 2:
            return "stable"

        delta = values[-1] - values[0]

        if delta > 2:
            return "up"

        if delta < -2:
            return "down"

        return "stable"
