from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    mode: str | None = None
