import type { MetricSummaryView } from "../dashboard.types";
import { formatScore } from "../utils/formatters";
import { trendFromSeries } from "../utils/trends";

type MetricBreakdownTableProps = {
  metrics: MetricSummaryView[];
};

const trendIcon = (series: Array<number | null>) => {
  const trend = trendFromSeries(series);

  if (trend === "Up") {
    return { icon: "↗", className: "text-emerald-300" };
  }

  if (trend === "Down") {
    return { icon: "↘", className: "text-rose-300" };
  }

  return { icon: "→", className: "text-orange-300" };
};

export const MetricBreakdownTable = ({ metrics }: MetricBreakdownTableProps) => (
  <div className="hud-panel grid min-h-0 grid-rows-[auto_minmax(0,1fr)] overflow-hidden p-[clamp(0.85rem,1.15vw,1.2rem)]">
    <p className="hud-title text-[clamp(1.05rem,1.35vw,1.55rem)] font-bold">Metric Breakdown</p>
    <div className="mt-[clamp(0.45rem,0.8vh,0.75rem)] grid min-h-0 grid-rows-[auto_minmax(0,1fr)] overflow-hidden rounded border border-cyan-300/12">
      <div className="grid grid-cols-[minmax(0,1.35fr)_repeat(4,minmax(0,1fr))] bg-cyan-400/8 px-[clamp(0.7rem,1vw,1rem)] py-[clamp(0.4rem,0.75vh,0.65rem)] text-[clamp(0.72rem,0.8vw,0.85rem)] font-bold uppercase text-cyan-200">
        <span>Metric</span>
        <span>Avg</span>
        <span>Min</span>
        <span>Max</span>
        <span>Trend</span>
      </div>
      <div className="grid min-h-0 content-stretch overflow-hidden">
        {metrics.map((metric) => {
          const trend = trendIcon(metric.series);

          return (
            <div
              key={metric.key}
              className="grid min-h-0 grid-cols-[minmax(0,1.35fr)_repeat(4,minmax(0,1fr))] items-center border-t border-cyan-300/10 px-[clamp(0.7rem,1vw,1rem)] py-[clamp(0.38rem,0.75vh,0.65rem)] text-[clamp(0.82rem,0.95vw,1rem)] leading-tight text-[#f2fbff]"
            >
              <span className={`truncate font-semibold ${metric.tone.valueClass}`}>{metric.label}</span>
              <span>{formatScore(metric.summary?.avg)}</span>
              <span>{formatScore(metric.summary?.min)}</span>
              <span>{formatScore(metric.summary?.max)}</span>
              <span className={`text-[clamp(1.2rem,1.5vw,1.6rem)] font-bold leading-none ${trend.className}`}>{trend.icon}</span>
            </div>
          );
        })}
      </div>
    </div>
  </div>
);
