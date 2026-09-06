import type { LiveMetric, LiveSnapshot, ReportView } from "../../domain/sessionAnalysis";
import { METRIC_CONFIG, METRIC_ORDER } from "./config/metrics.config";
import type {
  CoachingMode,
  MetricSummaryView,
  MetricView,
  SessionInfo,
  SessionSource,
  TimelineSeries,
} from "./dashboard.types";
import { scoreStatus } from "./utils/score";
import { trendFromSeries } from "./utils/trends";

const liveMetricValue = (metrics: LiveMetric[], key: (typeof METRIC_ORDER)[number]) =>
  metrics.find((metric) => metric.key === key)?.value ?? null;

const sessionStatusLabel = (score: number | null | undefined) => {
  const status = scoreStatus(score);
  return status === "Waiting" ? status : status.toUpperCase();
};

export const buildLiveMetricViews = (liveData: LiveSnapshot | null, history: LiveSnapshot[]): MetricView[] =>
  METRIC_ORDER.map((key) => {
    const config = METRIC_CONFIG[key];
    const series = history
      .map((snapshot) => liveMetricValue(snapshot.metrics, key))
      .filter((value): value is number => typeof value === "number");
    const value = liveData ? liveMetricValue(liveData.metrics, key) : null;

    return {
      key,
      label: config.label,
      value,
      series,
      status: trendFromSeries(series),
      tone: config.tone,
    };
  });

export const buildMetricSummaryViews = (report: ReportView | null): MetricSummaryView[] =>
  METRIC_ORDER.map((key) => {
    const config = METRIC_CONFIG[key];

    return {
      key,
      label: config.label,
      summary: report?.metrics[key] ?? null,
      series: report?.series[key] ?? [],
      tone: config.tone,
    };
  });

export const buildOverallTimeline = (report: ReportView | null): TimelineSeries[] => [
  {
    name: "Overall Score",
    values: report?.series.overall ?? report?.timeline.map((point) => point.overallScore) ?? [],
    color: "#19e6a1",
    times: report?.timeline.map((point) => point.time) ?? [],
  },
];

export const buildMultiMetricTimeline = (report: ReportView | null): TimelineSeries[] => [
  ...buildOverallTimeline(report),
  ...METRIC_ORDER.map((key) => ({
    name: METRIC_CONFIG[key].label,
    values: report?.series[key] ?? [],
    color: METRIC_CONFIG[key].tone.line,
    times: report?.timeline.map((point) => point.time) ?? [],
  })),
];

export const buildSessionInfo = ({
  source,
  coachingMode,
  customScenario,
  elapsedSeconds,
  liveData,
  isCameraReady,
  isMicReady,
  isAnalyzing,
}: {
  source: SessionSource;
  coachingMode: CoachingMode | null;
  customScenario: string;
  elapsedSeconds: number;
  liveData: LiveSnapshot | null;
  isCameraReady: boolean;
  isMicReady: boolean;
  isAnalyzing: boolean;
}): SessionInfo => ({
  overallScore: liveData?.overallScore ?? null,
  statusLabel: sessionStatusLabel(liveData?.overallScore),
  source,
  coachingMode,
  customScenario,
  elapsedSeconds,
  trackingStatus: isAnalyzing ? "Tracking" : "Idle",
  cameraStatus: source === "live_camera" ? (isCameraReady ? "Ready" : "Waiting") : "Not used",
  micStatus: source === "live_camera" ? (isMicReady ? "Ready" : "Waiting") : "Not used",
});
