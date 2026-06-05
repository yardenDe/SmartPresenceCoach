import type { DashboardState, SessionSource } from "../dashboard.types";
import type { RecentSession } from "../../../domain/sessionAnalysis";
import { formatDuration } from "../utils/formatters";
import { RecentSessions } from "./RecentSessions";
import { SessionControls } from "./SessionControls";
import { SourceSelector } from "./SourceSelector";

type LeftRailProps = {
  state: DashboardState;
  source: SessionSource | null;
  elapsedSeconds: number;
  uploadedVideoName: string;
  recentSessions: RecentSession[];
  canStart: boolean;
  canGenerateReport: boolean;
  canSendReportEmail: boolean;
  canDownloadReportPdf: boolean;
  isStarting: boolean;
  isStopping: boolean;
  isReportGenerating: boolean;
  isEmailSending: boolean;
  onSourceChange: (source: SessionSource) => void;
  onFileChange: (file: File) => void;
  onStart: () => void;
  onEnd: () => void;
  onNewSession: () => void;
  onDetailed: () => void;
  onBackToSummary: () => void;
  onDownloadPdf: () => void;
  onSendEmail: (email: string) => void;
};

const statusLabel: Record<DashboardState, string> = {
  setup: "Setup",
  live: "Live",
  offline_processing: "Processing",
  summary: "Complete",
  detailed: "Report",
};

export const LeftRail = ({
  state,
  source,
  elapsedSeconds,
  uploadedVideoName,
  recentSessions,
  canStart,
  canGenerateReport,
  canSendReportEmail,
  canDownloadReportPdf,
  isStarting,
  isStopping,
  isReportGenerating,
  isEmailSending,
  onSourceChange,
  onFileChange,
  onStart,
  onEnd,
  onNewSession,
  onDetailed,
  onBackToSummary,
  onDownloadPdf,
  onSendEmail,
}: LeftRailProps) => (
  <aside className="grid min-h-0 gap-[1vh] overflow-hidden xl:grid-rows-[auto_auto_auto_minmax(0,1fr)]">
    <div className="hud-panel grid content-start gap-[clamp(0.9rem,1.6vh,1.25rem)] p-[clamp(0.95rem,1.25vw,1.25rem)]">
      <div className="flex items-center justify-between">
        <p className="hud-label text-[clamp(0.95rem,1.05vw,1.1rem)]">Session</p>
        <span className="rounded border border-emerald-300/35 bg-emerald-400/10 px-[clamp(0.75rem,1vw,1rem)] py-[clamp(0.35rem,0.65vh,0.55rem)] text-[clamp(0.85rem,0.95vw,1rem)] font-bold uppercase text-emerald-300">
          {statusLabel[state]}
        </span>
      </div>
      <div>
        <p className="hud-title text-[clamp(1.75rem,2.55vw,2.65rem)] font-bold leading-tight">
          {state === "setup" ? "Standby" : state === "live" ? "Active" : state === "offline_processing" ? "Working" : "Completed"}
        </p>
        <p className="mt-2 text-[clamp(1rem,1.12vw,1.18rem)] font-medium leading-6 text-[#d8f3ff]">
          {state === "setup" ? "Choose your setup" : state === "live" ? "Session in progress" : state === "offline_processing" ? "Analyzing uploaded video" : "Session completed"}
        </p>
      </div>
      <div className="grid place-items-center rounded-md border border-cyan-300/14 bg-cyan-400/5 px-[clamp(0.75rem,1vw,1rem)] py-[clamp(0.9rem,1.8vh,1.35rem)] text-center shadow-[0_0_24px_rgba(34,211,238,0.08)]">
        <p className="hud-value font-mono text-[clamp(3.25rem,5.8vw,5.7rem)] font-bold leading-none tabular-nums tracking-normal">
          {formatDuration(elapsedSeconds)}
        </p>
        <p className="hud-label mt-[clamp(0.45rem,0.9vh,0.7rem)] text-[clamp(0.9rem,1vw,1.05rem)]">Elapsed</p>
      </div>
    </div>

    <SourceSelector
      source={source}
      disabled={state !== "setup"}
      uploadedVideoName={uploadedVideoName}
      onSourceChange={onSourceChange}
      onFileChange={onFileChange}
    />

    <SessionControls
      state={state}
      canStart={canStart}
      canGenerateReport={canGenerateReport}
      canSendReportEmail={canSendReportEmail}
      canDownloadReportPdf={canDownloadReportPdf}
      isStarting={isStarting}
      isStopping={isStopping}
      isReportGenerating={isReportGenerating}
      isEmailSending={isEmailSending}
      onStart={onStart}
      onEnd={onEnd}
      onNewSession={onNewSession}
      onDetailed={onDetailed}
      onBackToSummary={onBackToSummary}
      onDownloadPdf={onDownloadPdf}
      onSendEmail={onSendEmail}
    />

    <RecentSessions sessions={recentSessions} />
  </aside>
);
