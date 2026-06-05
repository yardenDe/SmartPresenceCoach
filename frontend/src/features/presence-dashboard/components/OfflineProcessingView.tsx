import type { MetricView, ProcessingStep, SessionInfo } from "../dashboard.types";
import { formatSource } from "../utils/formatters";
import { EmptyState } from "./EmptyState";
import { LoadingState } from "./LoadingState";
import { SessionInfoPanel } from "./SessionInfoPanel";

type OfflineProcessingViewProps = {
  step: ProcessingStep;
  percent: number;
  sessionInfo: SessionInfo;
  metrics: MetricView[];
};

const stepLabel: Record<ProcessingStep, string> = {
  uploading: "Uploading",
  analyzing_video: "Analyzing video",
  extracting_metrics: "Extracting metrics",
  generating_summary: "Generating summary",
  finalizing: "Finalizing",
};

export const OfflineProcessingView = ({ step, percent, sessionInfo, metrics }: OfflineProcessingViewProps) => (
  <>
    <div className="hud-panel grid min-h-0 place-items-center p-[clamp(1rem,1.5vw,1.6rem)]">
      <div className="w-[min(88%,44rem)]">
        <LoadingState title="Processing Uploaded Video" message={`${stepLabel[step]} for ${formatSource(sessionInfo.source)}.`} />
        <div className="mt-5 overflow-hidden rounded border border-cyan-300/18 bg-[#071723]">
          <div className="h-3 rounded bg-gradient-to-r from-emerald-400 to-cyan-400" style={{ width: `${Math.max(0, Math.min(100, percent))}%` }} />
        </div>
        <p className="mt-3 text-center text-sm font-semibold uppercase text-cyan-200">{percent}% complete</p>
      </div>
    </div>
    <SessionInfoPanel info={sessionInfo} />
    <div className="hud-panel min-h-0 p-[clamp(0.75rem,1vw,1rem)] xl:col-span-2">
      <EmptyState title="Metrics pending" message="Metrics will appear after processing completes." />
      <div className="hidden">{metrics.length}</div>
    </div>
  </>
);
