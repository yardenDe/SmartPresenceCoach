import { useEffect } from "react";

import { useAuth } from "../../hooks/useAuth";
import { buildSessionInfo } from "./dashboard.adapters";
import type { SessionSource } from "./dashboard.types";
import { DashboardShell } from "./components/DashboardShell";
import { LeftRail } from "./components/LeftRail";
import { MainWorkspace } from "./components/MainWorkspace";
import { useMetricSeries } from "./hooks/useMetricSeries";
import { usePresenceDashboard } from "./hooks/usePresenceDashboard";
import { useSessionLifecycle } from "./hooks/useSessionLifecycle";

export const PresenceDashboard = () => {
  const { username } = useAuth();
  const dashboard = usePresenceDashboard();
  const lifecycle = useSessionLifecycle();
  const source = dashboard.source ?? "live_camera";
  const isOffline = source === "uploaded_video";
  const report = lifecycle.finalReport;
  const metrics = useMetricSeries(lifecycle.liveData, lifecycle.liveHistory, report);

  useEffect(() => {
    if (lifecycle.finalReport && dashboard.dashboardState === "live") {
      dashboard.setDashboardState("summary");
    }
  }, [dashboard, lifecycle.finalReport]);

  useEffect(() => {
    if (lifecycle.finalReport && dashboard.dashboardState === "offline_processing") {
      dashboard.setProcessingPercent(100);
      dashboard.setProcessingStep("finalizing");
      dashboard.setDashboardState("summary");
    }
  }, [dashboard, lifecycle.finalReport]);

  const sessionInfo = buildSessionInfo({
    source,
    coachingMode: dashboard.coachingMode,
    customScenario: dashboard.customScenario,
    elapsedSeconds: lifecycle.sessionSeconds,
    liveData: lifecycle.liveData,
    isCameraReady: lifecycle.isCameraReady,
    isMicReady: lifecycle.isMicReady,
    isAnalyzing: lifecycle.isAnalyzing,
  });

  const statusMessage =
    lifecycle.error ??
    lifecycle.reportError ??
    lifecycle.reportMessage ??
    (lifecycle.isAnalyzing ? "All systems normal." : "Waiting for measurements.");

  const handleSourceChange = (nextSource: SessionSource) => {
    dashboard.setSource(nextSource);
    lifecycle.chooseMode(nextSource === "live_camera" ? "live" : "offline");
  };

  const handleStart = () => {
    if (!dashboard.canStart || !dashboard.source) {
      return;
    }

    const mode =
      dashboard.coachingMode === "custom"
        ? dashboard.customScenario
        : dashboard.coachingMode;

    if (dashboard.source === "uploaded_video") {
      dashboard.setDashboardState("offline_processing");
      dashboard.setProcessingStep("uploading");
      dashboard.setProcessingPercent(18);
      void lifecycle.startSession("offline", mode);
      window.setTimeout(() => dashboard.setProcessingStep("analyzing_video"), 600);
      window.setTimeout(() => dashboard.setProcessingPercent(42), 900);
      window.setTimeout(() => dashboard.setProcessingStep("extracting_metrics"), 1400);
      window.setTimeout(() => dashboard.setProcessingPercent(68), 1700);
      window.setTimeout(() => dashboard.setProcessingStep("generating_summary"), 2200);
      return;
    }

    dashboard.setDashboardState("live");
    void lifecycle.startSession("live", mode);
  };

  const handleEnd = async () => {
    await lifecycle.stopSession();
  };

  const handleNewSession = () => {
    lifecycle.resetSession();
    dashboard.resetSetup();
  };

  const handleDetailed = async () => {
    await lifecycle.generateFinalReport();
    dashboard.setDashboardState("detailed");
  };

  const leftRail = (
    <LeftRail
      state={dashboard.dashboardState}
      source={dashboard.source}
      elapsedSeconds={lifecycle.sessionSeconds}
      uploadedVideoName={lifecycle.offlineVideoName}
      recentSessions={lifecycle.recentSessions}
      canStart={dashboard.canStart && (source === "live_camera" || lifecycle.isOfflineVideoReady)}
      canGenerateReport={lifecycle.canGenerateReport}
      canSendReportEmail={lifecycle.canSendReportEmail}
      canDownloadReportPdf={lifecycle.canDownloadReportPdf}
      isStarting={lifecycle.isStarting}
      isStopping={lifecycle.isStopping}
      isReportGenerating={lifecycle.isReportGenerating}
      isEmailSending={lifecycle.isEmailSending}
      onSourceChange={handleSourceChange}
      onFileChange={lifecycle.loadOfflineVideo}
      onStart={handleStart}
      onEnd={handleEnd}
      onNewSession={handleNewSession}
      onDetailed={handleDetailed}
      onBackToSummary={() => dashboard.setDashboardState("summary")}
      onDownloadPdf={() => void lifecycle.downloadReportPdf()}
      onSendEmail={(email) => {
        if (email) {
          void lifecycle.sendReportEmail(email);
        }
      }}
    />
  );

  const workspace = (
    <MainWorkspace
      state={dashboard.dashboardState}
      selectedMode={dashboard.coachingMode}
      customScenario={dashboard.customScenario}
      sessionInfo={sessionInfo}
      liveMetrics={metrics.liveMetrics}
      summaryMetrics={metrics.summaryMetrics}
      overallTimeline={metrics.overallTimeline}
      multiMetricTimeline={metrics.multiMetricTimeline}
      reportScore={report?.overallScore ?? null}
      duration={report?.timeline[report.timeline.length - 1]?.time ?? lifecycle.sessionSeconds}
      trend={report?.overall?.trend}
      minScore={report?.overall?.min}
      maxScore={report?.overall?.max}
      summary={report?.summary}
      recommendations={report?.recommendations}
      processingStep={dashboard.processingStep}
      processingPercent={dashboard.processingPercent}
      isAnalyzing={lifecycle.isAnalyzing}
      isOffline={isOffline}
      liveDataReady={Boolean(lifecycle.liveData)}
      statusMessage={statusMessage}
      error={lifecycle.error}
      canDownloadReportPdf={lifecycle.canDownloadReportPdf}
      canSendReportEmail={lifecycle.canSendReportEmail}
      isReportGenerating={lifecycle.isReportGenerating}
      isEmailSending={lifecycle.isEmailSending}
      attachVideoElement={lifecycle.attachVideoElement}
      attachCanvasElement={lifecycle.attachLandmarksCanvasElement}
      onModeChange={dashboard.setCoachingMode}
      onCustomScenarioChange={dashboard.setCustomScenario}
      onBackToSummary={() => dashboard.setDashboardState("summary")}
      onNewSession={handleNewSession}
      onDownloadPdf={() => void lifecycle.downloadReportPdf()}
      onSendEmail={(email) => {
        if (email) {
          void lifecycle.sendReportEmail(email);
        }
      }}
    />
  );

  return (
    <DashboardShell
      state={dashboard.dashboardState}
      username={username}
      leftRail={leftRail}
      workspace={workspace}
    />
  );
};
