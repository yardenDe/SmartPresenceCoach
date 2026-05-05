from fastapi import APIRouter

from core.exceptions import FeatureNotImplementedError


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
async def list_reports() -> dict[str, str]:
    raise FeatureNotImplementedError()


@router.get("/{session_id}")
async def get_report_by_session(session_id: str) -> dict[str, str]:
    raise FeatureNotImplementedError()
