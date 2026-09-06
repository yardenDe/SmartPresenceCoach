export type AnalyzerMode = "live" | "offline";

export const METRIC_KEYS = [
  "focus",
  "posture",
  "presence",
  "engagement",
  "composure",
] as const;

export type MetricKey = (typeof METRIC_KEYS)[number];

export type BackendAnalysisScores = Partial<Record<MetricKey, number | null>>;

export type BackendScores = BackendAnalysisScores & {
  overall?: number | null;
};

export type BackendLiveResponse = {
  session_id: number;
  timestamp: number;
  scores: BackendScores;
};

export type BackendOfflineResponse = {
  session_id: number;
  status: string;
};

export type BackendMetricSummary = {
  avg: number | null;
  min: number | null;
  max: number | null;
  trend?: string | null;
};

export type BackendOverallSummary = {
  avg: number;
  min: number;
  max: number;
  trend: string;
};

export type BackendTimeSeries = {
  timestamps_sec: number[];
  series: Record<string, Array<number | null>>;
};

export type BackendReportResponse = {
  session_id: number;
  overall_score: number;
  scores: Record<string, BackendMetricSummary>;
  score_series: BackendTimeSeries;
  visual_metrics?: Record<string, BackendMetricSummary>;
  audio_metrics?: Record<string, BackendMetricSummary>;
  metric_series?: BackendTimeSeries;
  transcript?: string | null;
  summary?: string;
  recommendations?: string;
};

export type ReportEmailResponse = {
  status: string;
};

export type RecentSession = {
  session_id: number;
  mode: string | null;
  started_at: string | null;
  ended_at: string | null;
  overall_score: number | null;
  generated_at: string | null;
};

export type LiveMetric = {
  key: MetricKey;
  value: number | null;
};

export type LiveSnapshot = {
  sessionId: number;
  timestamp: number;
  overallScore: number;
  metrics: LiveMetric[];
};

export type TimelinePoint = {
  id: string;
  time: number;
  overallScore: number;
};

export type ReportView = {
  kind: "short" | "full" | "progress";
  sessionId?: number;
  overallScore: number;
  overall: BackendOverallSummary | null;
  metrics: Record<string, BackendMetricSummary>;
  timeline: TimelinePoint[];
  series: Record<string, Array<number | null>>;
  summary?: string;
  recommendations?: string;
};

const clampScore = (value: number | null | undefined) =>
  Math.max(0, Math.min(100, Math.round(value ?? 0)));

const liveMetricsFromScores = (scores: BackendAnalysisScores = {}): LiveMetric[] =>
  METRIC_KEYS.map((key) => ({
    key,
    value: scores[key] == null ? null : clampScore(scores[key]),
  }));

export const toLiveSnapshot = (response: BackendLiveResponse): LiveSnapshot => ({
  sessionId: response.session_id,
  timestamp: response.timestamp,
  overallScore: clampScore(response.scores.overall),
  metrics: liveMetricsFromScores(response.scores),
});

export const toReportView = (response: BackendReportResponse): ReportView => {
  const overallSeries = response.score_series.series.overall ?? [];
  const { overall, ...scores } = response.scores;
  const isFull = Boolean(response.summary || response.recommendations);

  return {
    kind: isFull ? "full" : "short",
    sessionId: response.session_id,
    overallScore: clampScore(response.overall_score),
    overall: (overall as BackendOverallSummary | undefined) ?? null,
    metrics: scores,
    series: response.score_series.series,
    timeline: response.score_series.timestamps_sec.map((time, index) => ({
      id: `report-${index + 1}`,
      time: Math.round(time),
      overallScore: clampScore(overallSeries[index]),
    })),
    summary: response.summary,
    recommendations: response.recommendations,
  };
};

export const buildProgressReport = (snapshots: LiveSnapshot[]): ReportView | null => {
  if (!snapshots.length) {
    return null;
  }

  const overallScores = snapshots.map((snapshot) => snapshot.overallScore);
  const average =
    overallScores.reduce((total, score) => total + score, 0) / overallScores.length;

  return {
    kind: "progress",
    overallScore: clampScore(average),
    overall: null,
    metrics: {},
    series: { overall: overallScores },
    timeline: snapshots.map((snapshot, index) => ({
      id: `live-${index + 1}`,
      time: Math.round(snapshot.timestamp),
      overallScore: snapshot.overallScore,
    })),
  };
};
