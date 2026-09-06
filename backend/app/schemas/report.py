from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ScoreSummary(BaseModel):
    avg: float | None = None
    min: float | None = None
    max: float | None = None
    trend: str | None = None


class MetricSummary(BaseModel):
    avg: float | None = None
    min: float | None = None
    max: float | None = None
    unit: str
    target_min: float
    target_max: float


class TimeSeries(BaseModel):
    timestamps_sec: list[float]
    series: dict[str, list[float | None]]


class ShortReportResponse(BaseModel):
    session_id: int
    overall_score: float
    scores: dict[str, ScoreSummary] = Field(default_factory=dict)
    score_series: TimeSeries


class FullReportResponse(ShortReportResponse):
    visual_metrics: dict[str, MetricSummary]
    audio_metrics: dict[str, MetricSummary]
    metric_series: TimeSeries
    summary: str
    recommendations: str
    transcript: str | None = None


class LLMReportText(BaseModel):
    summary: str
    recommendations: str


class ReportEmailRequest(BaseModel):
    to: str


class ReportEmailResponse(BaseModel):
    status: Literal["sent"]


class RecentReportResponse(BaseModel):
    session_id: int
    mode: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    overall_score: float | None = None
    generated_at: datetime | None = None
