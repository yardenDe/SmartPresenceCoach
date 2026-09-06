from analytics.config import METRIC_DEFINITIONS
from analytics.math_utils import average_available
from analytics.score_calculator import ScoreCalculator
from core.exceptions import (
    LLMUnavailableError,
    ReportNotFoundError,
    SnapshotsNotFoundError,
)
from core.logger import get_logger
from llm.prompts import session_report_prompt, session_report_system_instruction
from repositories.report_repository import ReportRepository
from repositories.snapshot_repository import SnapshotRepository
from schemas.analysis import AudioMetrics, Scores, VisualMetrics
from schemas.report import (
    FullReportResponse,
    LLMReportText,
    MetricSummary,
    ScoreSummary,
    ShortReportResponse,
    TimeSeries,
)
from services.llm_service import LLMService
from services.session_service import SessionService

logger = get_logger("app.reports")

SCORE_NAMES = tuple(Scores.model_fields)
VISUAL_METRIC_NAMES = tuple(VisualMetrics.model_fields)
AUDIO_METRIC_NAMES = tuple(
    name for name in AudioMetrics.model_fields if name != "transcript"
)
METRIC_NAMES = (*VISUAL_METRIC_NAMES, *AUDIO_METRIC_NAMES)


class ReportService:
    def __init__(
        self,
        session_service: SessionService,
        snapshot_repository: SnapshotRepository,
        report_repository: ReportRepository,
        score_calculator: ScoreCalculator,
    ):
        self.session_service = session_service
        self.snapshot_repository = snapshot_repository
        self.report_repository = report_repository
        self.score_calculator = score_calculator

    def generate_report(
        self,
        user_id: int,
        session_id: int,
        full: bool,
        llm_service: LLMService | None = None,
        require_saved_coaching: bool = False,
    ) -> ShortReportResponse | FullReportResponse:
        session = self.session_service.require_owned_session(user_id, session_id)

        if full:
            saved_report = self.report_repository.get_by_session(session_id)
            if require_saved_coaching and saved_report is None:
                raise ReportNotFoundError()

        rows = self._load_rows(session_id)
        score_series = self._build_score_series(rows)
        short_report = self._build_short_report(session_id, score_series)

        if not full:
            return short_report

        return self._build_full_report(
            short_report=short_report,
            rows=rows,
            mode=session.mode,
            llm_service=llm_service,
            saved_coaching=(
                LLMReportText(
                    summary=saved_report.summary,
                    recommendations=saved_report.recommendations,
                )
                if saved_report
                else None
            ),
        )

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

    def get_full_report_data(self, user_id: int, session_id: int) -> dict:
        report = self.generate_report(
            user_id=user_id,
            session_id=session_id,
            full=True,
            llm_service=None,
            require_saved_coaching=True,
        )
        return report.model_dump()

    def _load_rows(self, session_id: int) -> list[dict]:
        rows = self.snapshot_repository.get_metric_values(
            [*METRIC_NAMES, "transcript"],
            session_id,
        )
        if not rows:
            raise SnapshotsNotFoundError()
        return rows

    def _build_score_series(self, rows: list[dict]) -> TimeSeries:
        series = {name: [] for name in SCORE_NAMES}

        for row in rows:
            scores = self._calculate_scores(row)
            for name in SCORE_NAMES:
                series[name].append(getattr(scores, name) if scores else None)

        if not any(value is not None for value in series["overall"]):
            raise SnapshotsNotFoundError()

        return TimeSeries(
            timestamps_sec=[row["timestamp"] for row in rows],
            series=series,
        )

    def _calculate_scores(self, row: dict) -> Scores | None:
        return self.score_calculator.calculate(
            visual=VisualMetrics.model_validate(row),
            audio=AudioMetrics.model_validate(row),
        )

    def _build_short_report(
        self,
        session_id: int,
        score_series: TimeSeries,
    ) -> ShortReportResponse:
        scores = {
            name: self._summarize_score(score_series.series[name])
            for name in SCORE_NAMES
        }

        return ShortReportResponse(
            session_id=session_id,
            overall_score=scores["overall"].avg,
            scores=scores,
            score_series=score_series,
        )

    def _summarize_score(self, values: list[float | None]) -> ScoreSummary:
        available = self._available_values(values)
        return ScoreSummary(
            avg=average_available(available),
            min=min(available) if available else None,
            max=max(available) if available else None,
            trend=self._calculate_trend(available),
        )

    def _build_full_report(
        self,
        short_report: ShortReportResponse,
        rows: list[dict],
        mode: str | None,
        llm_service: LLMService | None,
        saved_coaching: LLMReportText | None,
    ) -> FullReportResponse:
        metric_series = self._build_metric_series(rows)
        transcripts = [row.get("transcript") for row in rows]
        coaching = self._get_coaching(
            session_id=short_report.session_id,
            overall_score=short_report.overall_score,
            metric_series=metric_series,
            transcripts=transcripts,
            mode=mode,
            llm_service=llm_service,
            saved_coaching=saved_coaching,
        )

        return FullReportResponse(
            **short_report.model_dump(),
            visual_metrics=self._summarize_metrics(
                metric_series,
                VISUAL_METRIC_NAMES,
            ),
            audio_metrics=self._summarize_metrics(
                metric_series,
                AUDIO_METRIC_NAMES,
            ),
            metric_series=metric_series,
            summary=coaching.summary,
            recommendations=coaching.recommendations,
            transcript=self._join_transcripts(transcripts),
        )

    @staticmethod
    def _build_metric_series(rows: list[dict]) -> TimeSeries:
        return TimeSeries(
            timestamps_sec=[row["timestamp"] for row in rows],
            series={
                name: [row.get(name) for row in rows]
                for name in METRIC_NAMES
            },
        )

    def _summarize_metrics(
        self,
        metric_series: TimeSeries,
        names: tuple[str, ...],
    ) -> dict[str, MetricSummary]:
        summaries = {}

        for name in names:
            values = self._available_values(
                metric_series.series[name]
            )
            definition = METRIC_DEFINITIONS[name]

            summaries[name] = MetricSummary(
                avg=average_available(values),
                min=min(values) if values else None,
                max=max(values) if values else None,
                unit=definition.unit,
                target_min=definition.target_min,
                target_max=definition.target_max,
            )

        return summaries

    def _get_coaching(
        self,
        session_id: int,
        overall_score: float,
        metric_series: TimeSeries,
        transcripts: list[str | None],
        mode: str | None,
        llm_service: LLMService | None,
        saved_coaching: LLMReportText | None,
    ) -> LLMReportText:
        if saved_coaching is not None:
            return saved_coaching

        if llm_service is None:
            return self._fallback_coaching()

        prompt = session_report_prompt(
            timestamps=metric_series.timestamps_sec,
            metric_vectors=metric_series.series,
            transcript_vector=transcripts,
            mode=mode,
        )

        try:
            coaching = llm_service.generate_json(
                prompt,
                LLMReportText,
                system_instruction=session_report_system_instruction(),
            )
        except LLMUnavailableError:
            logger.warning("event=report.llm_unavailable fallback=true")
            return self._fallback_coaching()

        self._save_coaching(session_id, overall_score, coaching)
        return coaching

    def _save_coaching(
        self,
        session_id: int,
        overall_score: float,
        coaching: LLMReportText,
    ) -> None:
        self.report_repository.create_report(
            session_id=session_id,
            overall_score=overall_score,
            summary=coaching.summary,
            recommendations=coaching.recommendations,
        )

    @staticmethod
    def _fallback_coaching() -> LLMReportText:
        return LLMReportText(
            summary="Your metric timeline was generated successfully, but the AI coaching summary is temporarily unavailable.",
            recommendations="Review the detailed charts, focus on your lowest average metric, and repeat the session later to generate the AI coaching text.",
        )

    @staticmethod
    def _join_transcripts(transcripts: list[str | None]) -> str | None:
        text = " ".join(
            transcript.strip()
            for transcript in transcripts
            if transcript and transcript.strip()
        )
        return text or None

    @staticmethod
    def _available_values(values: list[float | None]) -> list[float]:
        return [value for value in values if value is not None]

    @staticmethod
    def _calculate_trend(values: list[float]) -> str:
        if len(values) < 2:
            return "stable"
        delta = values[-1] - values[0]
        if delta > 2:
            return "up"
        if delta < -2:
            return "down"
        return "stable"
