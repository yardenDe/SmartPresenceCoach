import type {
  BackendMetricSummary,
  LiveSnapshot,
  MetricKey,
  RecentSession,
  ReportView,
} from "../../domain/sessionAnalysis";

export type DashboardState = "setup" | "live" | "offline_processing" | "summary" | "detailed";

export type SessionSource = "live_camera" | "uploaded_video";

export type CoachingMode = "speech" | "interview" | "presentation" | "custom";

export type ProcessingStep =
  | "uploading"
  | "analyzing_video"
  | "extracting_metrics"
  | "generating_summary"
  | "finalizing";

export type MetricTone = {
  line: string;
  valueClass: string;
  softClass: string;
  icon: string;
};

export type MetricView = {
  key: MetricKey;
  label: string;
  value: number | null;
  series: number[];
  status: string;
  tone: MetricTone;
};

export type MetricSummaryView = {
  key: MetricKey;
  label: string;
  summary: BackendMetricSummary | null;
  series: Array<number | null>;
  tone: MetricTone;
};

export type TimelineSeries = {
  name: string;
  values: Array<number | null>;
  color: string;
  times?: number[];
};

export type SessionInfo = {
  overallScore: number | null;
  statusLabel: string;
  source: SessionSource;
  coachingMode: CoachingMode | null;
  customScenario: string;
  elapsedSeconds: number;
  trackingStatus: string;
  cameraStatus: string;
  micStatus: string;
};

export type DashboardRuntime = {
  liveData: LiveSnapshot | null;
  liveHistory: LiveSnapshot[];
  finalReport: ReportView | null;
  recentSessions: RecentSession[];
  sessionSeconds: number;
  isAnalyzing: boolean;
  isStarting: boolean;
  isStopping: boolean;
  isCameraReady: boolean;
  isMicReady: boolean;
  isOfflineVideoReady: boolean;
  offlineVideoName: string;
  error: string | null;
  reportError: string | null;
  reportMessage: string | null;
  isReportGenerating: boolean;
  isEmailSending: boolean;
  canGenerateReport: boolean;
  canSendReportEmail: boolean;
  canDownloadReportPdf: boolean;
};
