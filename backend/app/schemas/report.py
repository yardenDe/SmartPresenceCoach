from datetime import datetime

from pydantic import BaseModel, Field


class ReportMetricSummary(BaseModel):
    avg: float | None
    min: float | None
    max: float | None


class ReportOverallSummary(BaseModel):
    avg: float
    min: float
    max: float
    trend: str


class ReportMetricTimeline(BaseModel):
    timestampsSec: list[float]
    series: dict[str, list[float | None]]


class ShortReportResponse(BaseModel):
    session_id: int
    overall_score: float
    overall_state: ReportOverallSummary | None = None
    timeline: ReportMetricTimeline | None = None
    metrics: dict[str, ReportMetricSummary] = Field(default_factory=dict)


class FullReportResponse(ShortReportResponse):
    summary: str
    recommendations: str


class LLMReportText(BaseModel):
    summary: str
    recommendations: str


class ReportEmailRequest(BaseModel):
    to: str


class ReportEmailResponse(BaseModel):
    status: str


class ReportResponse(BaseModel):
    session_id: int
    overall_score: float
    summary: str
    recommendations: str
    generated_at: datetime

    model_config = {"from_attributes": True}
