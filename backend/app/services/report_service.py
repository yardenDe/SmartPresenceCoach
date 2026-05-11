from core.exceptions import ResourceNotFoundError, SessionNotFoundError, UnauthorizedError
from core.logger import get_logger
from llm.prompts import session_report_prompt
from models.report import Report
from models.snapshot import Snapshot
from repositories.report_repository import ReportRepository
from repositories.session_repository import SessionRepository
from repositories.snapshot_repository import SnapshotRepository
from schemas.report import ReportLLMResponse
from services.llm_service import LLMService


class ReportNotFoundError(ResourceNotFoundError):
    code = "REPORT_NOT_FOUND"
    message = "Report not found"


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
        report_repository: ReportRepository,
        llm_service: LLMService,
    ):
        self.session_repository = session_repository
        self.snapshot_repository = snapshot_repository
        self.report_repository = report_repository
        self.llm_service = llm_service
        self.logger = get_logger("app.reports")


    def generate_report(self, session_id: int) -> Report:
       
        snapshots = self.snapshot_repository.list_by_session(session_id)
        metric_vectors, overall_score = self._create_metric_vectors(snapshots)

        prompt = session_report_prompt(
            overall_score=overall_score,
            metric_vectors=metric_vectors,
        )
        llm_result = self.llm_service.generate_json(
            prompt=prompt,
            response_model=ReportLLMResponse,
        )

        report = self.report_repository.create_report(
            session_id=session_id,
            overall_score=overall_score,
            summary=llm_result.summary,
            recommendations=llm_result.recommendations,
        )

        return report
    

    def _create_metric_vectors(
        self,
        snapshots: list[Snapshot],
    ) -> tuple[dict[str, list[float]], float]:
        
        vectors: dict[str, list[float]] = {
            metric: []
            for metric in self.METRICS
        }
        overall_score = 0.0

        for snapshot in snapshots:
            vectors["focus"].append(float(snapshot.focus))
            vectors["posture"].append(float(snapshot.posture))
            vectors["presence"].append(float(snapshot.presence))
            vectors["vitality"].append(float(snapshot.vitality))
            vectors["composure"].append(float(snapshot.composure))

            overall_score += float(snapshot.overall_score)

        if snapshots:
            overall_score = round(overall_score / len(snapshots), 2)

        return vectors, overall_score
