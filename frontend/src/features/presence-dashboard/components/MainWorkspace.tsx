import type { RefCallback } from "react";

import type {
  CoachingMode,
  DashboardState,
  MetricSummaryView,
  MetricView,
  ProcessingStep,
  SessionInfo,
  TimelineSeries,
} from "../dashboard.types";
import { DetailedReportView } from "./DetailedReportView";
import { LiveView } from "./LiveView";
import { OfflineProcessingView } from "./OfflineProcessingView";
import { SetupView } from "./SetupView";
import { SummaryView } from "./SummaryView";

type MainWorkspaceProps = {
  state: DashboardState;
  selectedMode: CoachingMode | null;
  customScenario: string;
  sessionInfo: SessionInfo;
  liveMetrics: MetricView[];
  summaryMetrics: MetricSummaryView[];
  overallTimeline: TimelineSeries[];
  multiMetricTimeline: TimelineSeries[];
  reportScore: number | null;
  duration: number;
  trend: string | undefined;
  minScore: number | null | undefined;
  maxScore: number | null | undefined;
  summary: string | undefined;
  recommendations: string | undefined;
  processingStep: ProcessingStep;
  processingPercent: number;
  isAnalyzing: boolean;
  isOffline: boolean;
  liveDataReady: boolean;
  statusMessage: string;
  error: string | null;
  canDownloadReportPdf: boolean;
  canSendReportEmail: boolean;
  isReportGenerating: boolean;
  isEmailSending: boolean;
  attachVideoElement: RefCallback<HTMLVideoElement>;
  attachCanvasElement: RefCallback<HTMLCanvasElement>;
  onModeChange: (mode: CoachingMode) => void;
  onCustomScenarioChange: (value: string) => void;
  onBackToSummary: () => void;
  onNewSession: () => void;
  onDownloadPdf: () => void;
  onSendEmail: (email: string) => void;
};

export const MainWorkspace = (props: MainWorkspaceProps) => {
  const commonClass =
    props.state === "setup"
      ? "grid h-full min-h-0 gap-[1vh]"
      : props.state === "detailed"
        ? "grid h-full min-h-0 gap-[1vh]"
      : props.state === "summary"
        ? "grid h-full min-h-0 gap-[1vh] xl:grid-cols-[minmax(0,76fr)_minmax(180px,14fr)] xl:grid-rows-[minmax(0,72fr)_minmax(150px,28fr)]"
        : "grid h-full min-h-0 gap-[1vh] xl:grid-cols-[minmax(0,76fr)_minmax(180px,14fr)] xl:grid-rows-[minmax(0,72fr)_minmax(150px,28fr)]";

  return (
    <main className={commonClass}>
      {props.state === "setup" ? (
        <SetupView
          selectedMode={props.selectedMode}
          customScenario={props.customScenario}
          onModeChange={props.onModeChange}
          onCustomScenarioChange={props.onCustomScenarioChange}
        />
      ) : null}
      {props.state === "live" ? (
        <LiveView
          isAnalyzing={props.isAnalyzing}
          isOffline={props.isOffline}
          liveDataReady={props.liveDataReady}
          statusMessage={props.statusMessage}
          error={props.error}
          metrics={props.liveMetrics}
          sessionInfo={props.sessionInfo}
          attachVideoElement={props.attachVideoElement}
          attachCanvasElement={props.attachCanvasElement}
        />
      ) : null}
      {props.state === "offline_processing" ? (
        <OfflineProcessingView
          step={props.processingStep}
          percent={props.processingPercent}
          sessionInfo={props.sessionInfo}
          metrics={props.liveMetrics}
        />
      ) : null}
      {props.state === "summary" ? (
        <SummaryView
          reportScore={props.reportScore}
          duration={props.duration}
          trend={props.trend}
          minScore={props.minScore}
          maxScore={props.maxScore}
          timeline={props.overallTimeline}
          metrics={props.summaryMetrics}
        />
      ) : null}
      {props.state === "detailed" ? (
        <DetailedReportView
          timeline={props.multiMetricTimeline}
          metrics={props.summaryMetrics}
          summary={props.summary}
          recommendations={props.recommendations}
        />
      ) : null}
    </main>
  );
};
