import type { MetricSummaryView } from "../dashboard.types";
import { formatScore } from "../utils/formatters";
import { Sparkline } from "./Sparkline";

type MetricSummaryCardProps = {
  metric: MetricSummaryView;
};

export const MetricSummaryCard = ({ metric }: MetricSummaryCardProps) => {
  const hasSparkline = metric.series.filter((value): value is number => typeof value === "number").length > 1;

  return (
    <div className="hud-card grid min-h-0 content-center overflow-hidden p-[clamp(0.95rem,1.25vw,1.35rem)]">
      <p className={`hud-title text-[clamp(1.2rem,1.55vw,1.75rem)] font-bold leading-tight ${metric.tone.valueClass}`}>
        {metric.label}
      </p>
      <div className="mt-[clamp(0.8rem,1.25vh,1.15rem)] grid grid-cols-3 items-end gap-[clamp(0.65rem,1vw,1.25rem)] text-[clamp(0.9rem,1vw,1.1rem)] leading-tight text-[#d8f3ff]/92">
        <span>
          Avg
          <strong className="mt-1 block text-[clamp(2rem,2.75vw,3rem)] leading-none text-white">{formatScore(metric.summary?.avg)}</strong>
        </span>
        <span>
          Mean
          <strong className="mt-1 block text-[clamp(2rem,2.75vw,3rem)] leading-none text-white">{formatScore(metric.summary?.avg)}</strong>
        </span>
        <span>
          Max
          <strong className="mt-1 block text-[clamp(2rem,2.75vw,3rem)] leading-none text-white">{formatScore(metric.summary?.max)}</strong>
        </span>
      </div>
      {hasSparkline ? (
        <div className="mt-[clamp(0.85rem,1.35vh,1.2rem)] h-[clamp(1.8rem,4.5vh,2.75rem)] min-h-0 overflow-hidden">
          <Sparkline values={metric.series} color={metric.tone.line} />
        </div>
      ) : null}
    </div>
  );
};
