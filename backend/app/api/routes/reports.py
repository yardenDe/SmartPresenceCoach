from fastapi import APIRouter, Depends, File, UploadFile

from core.dependencies import (
    get_current_user_id,
    get_report_service,
    get_llm_service,
    get_analysis_service,
    get_storage,
    get_session_service,
)
from schemas.report import (
    FullReportResponse,
    RecentReportResponse,
    ShortReportResponse,
)
from services.report_service import ReportService
from services.llm_service import LLMService
from services.analysis_service import AnalysisService
from services.session_service import SessionService
from media.storage import Storage
from media.media_reader import MediaReader
from db.models.analysis import Transcript
from core.exceptions import InvalidVideoError
import av

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/recent", response_model=list[RecentReportResponse])
def recent_reports(
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> list[RecentReportResponse]:
    return service.list_recent_reports(user_id=user_id)


@router.post("/{session_id}/short", response_model=ShortReportResponse)
def generate_short_report(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
) -> ShortReportResponse:
    return service.generate_report(
        user_id=user_id,
        session_id=session_id,
        full=False,
    )


@router.post("/{session_id}/full", response_model=FullReportResponse)
def generate_full_report(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ReportService = Depends(get_report_service),
    llm_service: LLMService | None = Depends(get_llm_service),
) -> FullReportResponse:
    return service.generate_report(
        user_id=user_id,
        session_id=session_id,
        full=True,
        llm_service=llm_service,
    )


@router.post("/{session_id}/transcript")
async def upload_transcript(
    session_id: int,
    video: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    session_service: SessionService = Depends(get_session_service),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    storage: Storage = Depends(get_storage),
    report_service: ReportService = Depends(get_report_service),
):
    session_service.require_owned_session(user_id, session_id)
    path = await storage.save_temp(video)
    try:
        try:
            segments = MediaReader(path).read_audio()
        except av.FFmpegError as exc:
            raise InvalidVideoError() from exc

        if not segments:
            raise InvalidVideoError("No audio found in the recording")

        records = []
        for segment in segments:
            text = analysis_service.transcribe(segment.data)
            if text:
                records.append(Transcript(
                    session_id=session_id,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    transcript=text,
                ))

        report_service.replace_transcripts(session_id, records)
        return {"transcript": " ".join(record.transcript for record in records) or None}
    finally:
        storage.delete(path)
