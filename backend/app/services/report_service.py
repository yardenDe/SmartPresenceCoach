from core.exceptions import SessionNotFoundError, SnapshotsNotFoundError, UnauthorizedError
from core.logger import get_logger
from repositories.session_repository import SessionRepository
from repositories.snapshot_repository import SnapshotRepository
from schemas.report import FullReportResponse, ShortReportResponse


class ReportService:
    METRICS = [
        "focus",
        "posture",
        "presence",
        "vitality",
        "composure",
    ]

    def __init__(
        self,
        session_repository: SessionRepository,
        snapshot_repository: SnapshotRepository,
    ):
        self.session_repository = session_repository
        self.snapshot_repository = snapshot_repository
        self.logger = get_logger("app.reports")

    def generate_short_report(self, user_id: int, session_id: int) -> ShortReportResponse:
        self._validate_session(user_id, session_id)
        return self._get_short_report(session_id)

    def generate_full_report(self, user_id: int, session_id: int) -> FullReportResponse:
        self._validate_session(user_id, session_id)
        short_report = self._get_short_report(session_id)
        detailed_timeline = self._get_detailed_timeline(session_id)

        return FullReportResponse.model_validate(
            {
                **short_report.model_dump(),
                "detailedTimeline": detailed_timeline,
            },
        )

    def _validate_session(self, user_id: int, session_id: int) -> None:
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

    def _get_short_report(self, session_id: int) -> ShortReportResponse:
        overall_timeline = self.snapshot_repository.get_overall_timeline(session_id)
        if not overall_timeline:
            raise SnapshotsNotFoundError()

        timestamps = [item["timestamp"] for item in overall_timeline]
        overall_scores = [item["overall"] for item in overall_timeline]
        
        all_metrics = ["overall"] + list(self.METRICS)
        metrics_states = self.snapshot_repository.get_metrics_stats(all_metrics, session_id)

        if not metrics_states or metrics_states.get("overall_avg") is None:
            raise SnapshotsNotFoundError()

        metrics = {}
        for metric in self.METRICS:
            metrics[metric] = {
                "avg": metrics_states[f"{metric}_avg"],
                "min": metrics_states[f"{metric}_min"],
                "max": metrics_states[f"{metric}_max"],
            }

        report_data = {
            "overall": {
                "avg": metrics_states["overall_avg"],
                "min": metrics_states["overall_min"],
                "max": metrics_states["overall_max"],
                "trend": self._trend(overall_scores),
            },
            "timeline": {
                "timestampsSec": timestamps,
                "overallScores": overall_scores,
            },
            "metrics": metrics,
        }

        return ShortReportResponse.model_validate(
            {
                "session_id": session_id,
                "overall_score": report_data["overall"]["avg"],
                **report_data,
            },
        )

    def _get_detailed_timeline(self, session_id: int) -> dict:
        metrics = ["overall"] + list(self.METRICS)
        rows = self.snapshot_repository.get_metric_vector_rows(session_id, metrics)
        if not rows:
            raise SnapshotsNotFoundError()

        timestamps = [float(row._mapping["timestamp"]) for row in rows]
        series = {
            metric: [
                float(row._mapping[metric])
                if row._mapping[metric] is not None
                else None
                for row in rows
            ]
            for metric in metrics
        }

        return {
            "timestampsSec": timestamps,
            "series": series,
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
