import type { MetricView } from "../dashboard.types";
import { formatScore } from "../utils/formatters";
import { Sparkline } from "./Sparkline";

type MetricCardProps = {
  metric: MetricView;
};

export const MetricCard = ({ metric }: MetricCardProps) => {
  const hasSparkline = metric.series.filter((value): value is number => typeof value === "number").length > 1;

  return (
    <div className="hud-card grid min-h-0 content-center overflow-hidden p-[clamp(0.95rem,1.25vw,1.35rem)]">
      <div className="grid grid-cols-[auto_minmax(0,1fr)] items-center gap-[clamp(0.8rem,1.05vw,1.2rem)]">
        <div className={`grid aspect-square w-[clamp(3.4rem,4.7vw,4.8rem)] place-items-center rounded-full ${metric.tone.softClass} ${metric.tone.valueClass}`}>
          <span className="text-[clamp(2.1rem,3vw,3rem)] font-bold leading-none">{metric.tone.icon}</span>
        </div>
        <div className="min-w-0">
          <p className="hud-label truncate text-[clamp(0.95rem,1.08vw,1.15rem)]">{metric.label}</p>
          <p className={`mt-1 text-[clamp(2.4rem,3.7vw,3.9rem)] font-bold leading-none tabular-nums ${metric.tone.valueClass}`}>
            {formatScore(metric.value)} <span className="text-[clamp(0.78rem,0.95vw,1rem)] text-[#b8dce8]">/100</span>
          </p>
          <p className="mt-[clamp(0.35rem,0.8vh,0.65rem)] text-[clamp(0.8rem,0.95vw,1rem)] font-semibold text-[#d8f3ff]/72">{metric.status}</p>
        </div>
      </div>
      {hasSparkline ? (
        <div className="mt-[clamp(0.75rem,1.3vh,1rem)] h-[clamp(1.75rem,4.4vh,2.75rem)] min-h-0 overflow-hidden">
          <Sparkline values={metric.series} color={metric.tone.line} />
        </div>
      ) : null}
    </div>
  );
};
