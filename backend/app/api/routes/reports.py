from fastapi import APIRouter


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
async def list_reports():
    return {"message": "Reports list endpoint"}


@router.get("/{session_id}")
async def get_report_by_session(session_id: str):
    return {"message": f"Report by session endpoint for {session_id}"}

