from fastapi import APIRouter

router = APIRouter(prefix="/live", tags=["live"])


@router.post("/frame")
async def analyze_frame():
    return {"message": "frame endpoint"}
