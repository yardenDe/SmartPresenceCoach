from pydantic import BaseModel

from schemas.analysis import AnalysisResponse


class LiveResponse(BaseModel):
    session_id: int
    result: AnalysisResponse
