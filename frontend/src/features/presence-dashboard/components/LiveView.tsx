import type { RefCallback } from "react";

import type { MetricView, SessionInfo } from "../dashboard.types";
import { EmptyState } from "./EmptyState";
import { MetricCard } from "./MetricCard";
import { SessionInfoPanel } from "./SessionInfoPanel";

type LiveViewProps = {
  isAnalyzing: boolean;
  isOffline: boolean;
  liveDataReady: boolean;
  statusMessage: string;
  error: string | null;
  metrics: MetricView[];
  sessionInfo: SessionInfo;
  attachVideoElement: RefCallback<HTMLVideoElement>;
  attachCanvasElement: RefCallback<HTMLCanvasElement>;
};

const availabilityIcon = (status: string) =>
  status === "Ready" || status === "Tracking" ? "🟢" : "🔴";

export const LiveView = ({
  isAnalyzing,
  isOffline,
  liveDataReady,
  statusMessage,
  error,
  metrics,
  sessionInfo,
  attachVideoElement,
  attachCanvasElement,
}: LiveViewProps) => (
  <>
    <div className="hud-panel relative min-h-0 overflow-hidden bg-[radial-gradient(circle_at_center,#162b3a_0%,#0c1a25_100%)]">
      <video
        ref={attachVideoElement}
        autoPlay={!isOffline}
        controls={isOffline}
        muted
        playsInline
        className="h-full w-full object-cover opacity-[0.9]"
      />
      <canvas ref={attachCanvasElement} className="pointer-events-none absolute inset-0 h-full w-full object-cover" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex items-center justify-between gap-4 border-t border-cyan-300/12 bg-[#08141d]/70 px-[clamp(1rem,1.5vw,1.5rem)] py-[clamp(0.7rem,1vh,0.95rem)] text-[clamp(0.9rem,1vw,1.05rem)] text-[#d8f3ff] backdrop-blur">
        <span className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-300" />
          Tracking
        </span>
        <span className="min-w-0 truncate">{statusMessage}</span>
        <span className="flex shrink-0 items-center gap-4">
          <span>{availabilityIcon(sessionInfo.cameraStatus)} Camera</span>
          <span>{availabilityIcon(sessionInfo.micStatus)} Mic</span>
        </span>
      </div>
      <div className="pointer-events-none absolute left-5 top-5 rounded border border-emerald-300/30 bg-emerald-400/12 px-4 py-2 text-base font-bold uppercase text-emerald-200">
        {isAnalyzing ? "Live" : "Ready"}
      </div>
      {error && !isAnalyzing ? (
        <div className="pointer-events-none absolute inset-0 grid place-items-center bg-[#061018]/45 px-6 text-center backdrop-blur-[1px]">
          <div className="hud-card max-w-lg px-5 py-4">
            <p className="hud-title text-3xl font-bold text-rose-100">Session did not start</p>
            <p className="mt-3 text-lg leading-8 text-rose-100/90">{error}</p>
          </div>
        </div>
      ) : null}
      {!isAnalyzing && !liveDataReady && !error ? (
        <EmptyState title="Ready to begin analysis" message="Start your session to analyze presence, posture and focus." />
      ) : null}
    </div>
    <SessionInfoPanel info={sessionInfo} />
    <div className="hud-panel grid min-h-0 grid-rows-[auto_minmax(0,1fr)] p-[clamp(0.75rem,1vw,1rem)] xl:col-span-2">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="hud-title text-[clamp(1.2rem,1.6vw,1.8rem)] font-bold">Live Metrics</h2>
        <span className="hud-label text-base">{liveDataReady ? "Live data" : "Waiting"}</span>
      </div>
      <div className="grid min-h-0 gap-[0.8vw] md:grid-cols-5">
        {metrics.map((metric) => (
          <MetricCard key={metric.key} metric={metric} />
        ))}
      </div>
    </div>
  </>
);
