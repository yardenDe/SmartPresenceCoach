from datetime import datetime

from pydantic import BaseModel, Field


class ReportMetricSummary(BaseModel):
    avg: float
    min: float
    max: float


class ReportOverallSummary(ReportMetricSummary):
    trend: str


class ReportTimeline(BaseModel):
    timestampsSec: list[float]
    overallScores: list[float]


class ReportMetricTimeline(BaseModel):
    timestampsSec: list[float]
    series: dict[str, list[float | None]]


class ShortReportResponse(BaseModel):
    session_id: int
    overall_score: float
    overall: ReportOverallSummary | None = None
    timeline: ReportTimeline | None = None
    metrics: dict[str, ReportMetricSummary] = Field(default_factory=dict)


class FullReportResponse(ShortReportResponse):
    detailedTimeline: ReportMetricTimeline


class ReportResponse(BaseModel):
    session_id: int
    overall_score: float
    summary: str
    recommendations: str
    generated_at: datetime

    model_config = {"from_attributes": True}
