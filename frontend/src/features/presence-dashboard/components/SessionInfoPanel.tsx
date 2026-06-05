import type { ReactNode } from "react";

import type { SessionInfo } from "../dashboard.types";
import { formatCoachingMode, formatDuration, formatSource } from "../utils/formatters";
import { OverallScoreCard } from "./OverallScoreCard";

type SessionInfoPanelProps = {
  info: SessionInfo;
  showOverallScore?: boolean;
  elapsedLabel?: string;
  actions?: ReactNode;
};

export const SessionInfoPanel = ({ info, showOverallScore = true, elapsedLabel = "Elapsed", actions }: SessionInfoPanelProps) => (
  <aside className={`hud-panel grid min-h-0 p-[clamp(1rem,1.35vw,1.35rem)] ${showOverallScore ? "grid-rows-[auto_minmax(0,1fr)]" : "content-start"}`}>
    {showOverallScore ? (
      <div className="grid min-h-0">
        <p className="hud-title text-[clamp(1.05rem,1.35vw,1.45rem)] font-bold">Overall Score</p>
        <div className="mt-[clamp(0.6rem,1vh,0.9rem)]">
          <OverallScoreCard score={info.overallScore} status={info.statusLabel} size="panel" />
        </div>
      </div>
    ) : (
      <p className="hud-title text-[clamp(1.05rem,1.35vw,1.45rem)] font-bold">Session Info</p>
    )}
    {actions ? <div className="mt-[clamp(0.8rem,1.4vh,1.1rem)] grid gap-[clamp(0.55rem,0.9vh,0.8rem)]">{actions}</div> : null}
    <div className={`${showOverallScore || actions ? "mt-[clamp(0.85rem,1.6vh,1.2rem)]" : "mt-5"} grid min-h-0 content-evenly gap-[clamp(0.55rem,1vh,0.85rem)] text-[clamp(1rem,1.1vw,1.14rem)] text-[#d8f3ff]/88`}>
      {[
        ["Mode", formatCoachingMode(info.coachingMode)],
        ["Source", formatSource(info.source)],
        [elapsedLabel, formatDuration(info.elapsedSeconds)],
        ["Tracking", info.trackingStatus],
        ["Camera", info.cameraStatus],
        ["Mic", info.micStatus],
      ].map(([label, value]) => (
        <div key={label} className="flex min-h-[clamp(2.15rem,4.8vh,2.95rem)] items-center justify-between gap-3 border-b border-cyan-300/10 pb-[clamp(0.45rem,0.8vh,0.7rem)] last:border-b-0">
          <span className="hud-label text-[clamp(0.86rem,0.98vw,1.02rem)]">{label}</span>
          <span className="truncate text-right text-[clamp(1rem,1.12vw,1.18rem)] font-semibold text-[#f2fbff]">{value}</span>
        </div>
      ))}
    </div>
  </aside>
);
