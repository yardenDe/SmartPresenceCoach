from pydantic import BaseModel

from schemas.analysis import AnalysisChunk


class OfflineVideoResponse(BaseModel):
    result: list[AnalysisChunk]
