from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/create")
async def create_session():
    return {"message": "Session created"}


@router.post("/{session_id}/start")
async def start_session(session_id: str):
    return {"message": f"Session {session_id} started"}


@router.post("/{session_id}/end")
async def end_session(session_id: str):
    return {"message": f"Session {session_id} ended"}


