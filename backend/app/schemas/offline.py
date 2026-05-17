from pydantic import BaseModel


class OfflineResponse(BaseModel):
    session_id: int
    status: str
