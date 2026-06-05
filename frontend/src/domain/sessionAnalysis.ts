export type AnalyzerMode = "live" | "offline";

export type MetricKey = "focus" | "posture" | "presence" | "engagement" | "composure";

export type MetricDefinition = {
  key: MetricKey;
  label: string;
};

export const METRICS: readonly MetricDefinition[] = [
  { key: "focus", label: "Focus" },
  { key: "posture", label: "Posture" },
  { key: "presence", label: "Presence" },
  { key: "engagement", label: "Engagement" },
  { key: "composure", label: "Composure" },
] as const;

export type BackendAnalysisScores = Partial<Record<MetricKey, number | null>>;

export type BackendAnalysisResult = {
  id: number;
  timestamp: number;
  frames_analyzed: number;
  overall: number;
  scores: BackendAnalysisScores;
};

export type BackendLiveResponse = {
  session_id: number;
  result: BackendAnalysisResult;
};

export type BackendOfflineResponse = {
  session_id: number;
  status: string;
};

export type BackendMetricSummary = {
  avg: number | null;
  min: number | null;
  max: number | null;
};

export type BackendOverallSummary = {
  avg: number;
  min: number;
  max: number;
  trend: string;
};

export type BackendReportTimeline = {
  timestampsSec: number[];
  series: Record<string, Array<number | null>>;
};

export type BackendReportResponse = {
  session_id: number;
  overall_score: number;
  overall_state: BackendOverallSummary | null;
  timeline: BackendReportTimeline | null;
  metrics: Record<string, BackendMetricSummary>;
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
  label: string;
  value: number;
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
  METRICS.map((metric) => ({
    ...metric,
    value: clampScore(scores[metric.key]),
  }));

export const toLiveSnapshot = (response: BackendLiveResponse): LiveSnapshot => ({
  sessionId: response.session_id,
  timestamp: response.result.timestamp,
  overallScore: clampScore(response.result.overall),
  metrics: liveMetricsFromScores(response.result.scores),
});

export const toReportView = (response: BackendReportResponse): ReportView => {
  const timeline = response.timeline ?? { timestampsSec: [], series: {} };
  const overallSeries = timeline.series.overall ?? [];
  const isFull = Boolean(response.summary || response.recommendations);

  return {
    kind: isFull ? "full" : "short",
    sessionId: response.session_id,
    overallScore: clampScore(response.overall_score),
    overall: response.overall_state,
    metrics: response.metrics ?? {},
    series: timeline.series,
    timeline: timeline.timestampsSec.map((time, index) => ({
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
