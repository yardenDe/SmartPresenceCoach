import type { DashboardState } from "../dashboard.types";

type SessionControlsProps = {
  state: DashboardState;
  canStart: boolean;
  canGenerateReport: boolean;
  isStarting: boolean;
  isStopping: boolean;
  isReportGenerating: boolean;
  onStart: () => void;
  onEnd: () => void;
  onNewSession: () => void;
  onDetailed: () => void;
  onBackToSummary: () => void;
};

export const SessionControls = ({
  state,
  canStart,
  canGenerateReport,
  isStarting,
  isStopping,
  isReportGenerating,
  onStart,
  onEnd,
  onNewSession,
  onDetailed,
  onBackToSummary,
}: SessionControlsProps) => (
  <div className="hud-panel grid min-h-fit content-start gap-3 p-[clamp(0.8rem,1.2vw,1rem)]">
    <p className="hud-label text-base">Controls</p>
    {state === "setup" ? (
      <>
        <button type="button" onClick={onStart} disabled={!canStart || isStarting} className="hud-button hud-button-primary px-5 py-3.5 text-lg disabled:opacity-50">
          {isStarting ? "Starting..." : "Start Session"}
        </button>
        <button type="button" disabled className="hud-button border-rose-400/45 px-5 py-3.5 text-lg text-rose-200 opacity-50">
          End Session
        </button>
      </>
    ) : null}
    {state === "live" ? (
      <button type="button" onClick={onEnd} disabled={isStopping} className="hud-button border-rose-400/45 px-5 py-3.5 text-lg text-rose-200 disabled:opacity-50">
        {isStopping ? "Stopping..." : "End Session"}
      </button>
    ) : null}
    {state === "offline_processing" ? (
      <>
        <button type="button" disabled className="hud-button px-5 py-3.5 text-lg opacity-50">
          Processing...
        </button>
        <button type="button" onClick={onNewSession} className="hud-button px-5 py-3.5 text-lg">
          New Session
        </button>
      </>
    ) : null}
    {state === "summary" ? (
      <>
        <button type="button" onClick={onNewSession} className="hud-button hud-button-primary px-5 py-3.5 text-lg">
          New Session
        </button>
        <button type="button" onClick={onDetailed} disabled={!canGenerateReport || isReportGenerating} className="hud-button px-5 py-3.5 text-lg disabled:opacity-50">
          {isReportGenerating ? "Generating..." : "View Detailed Analysis"}
        </button>
      </>
    ) : null}
    {state === "detailed" ? (
      <>
        <button type="button" onClick={onBackToSummary} className="hud-button px-5 py-3.5 text-lg">
          Back to Summary
        </button>
        <button type="button" onClick={onNewSession} className="hud-button hud-button-primary px-5 py-3.5 text-lg">
          New Session
        </button>
      </>
    ) : null}
  </div>
);
