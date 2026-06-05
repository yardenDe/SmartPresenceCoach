import type { MetricSummaryView, TimelineSeries } from "../dashboard.types";
import { formatDuration, formatScore } from "../utils/formatters";
import { EmptyState } from "./EmptyState";
import { MetricSummaryCard } from "./MetricSummaryCard";
import { OverallScoreCard } from "./OverallScoreCard";
import { TimelineChart } from "./TimelineChart";

type SummaryViewProps = {
  reportScore: number | null;
  duration: number;
  trend: string | undefined;
  minScore: number | null | undefined;
  maxScore: number | null | undefined;
  timeline: TimelineSeries[];
  metrics: MetricSummaryView[];
};

export const SummaryView = ({
  reportScore,
  duration,
  trend,
  minScore,
  maxScore,
  timeline,
  metrics,
}: SummaryViewProps) => (
  <>
    <div className="hud-panel grid min-h-0 grid-rows-[minmax(0,1fr)_auto] p-[clamp(1rem,1.4vw,1.5rem)] xl:col-span-2">
      <div className="grid min-h-0 gap-[1vw] xl:grid-cols-[minmax(180px,20fr)_minmax(0,80fr)]">
        <div className="grid min-h-0 place-items-center">
          <p className="hud-title mb-[clamp(0.7rem,1.2vh,1rem)] text-center text-[clamp(1.3rem,1.75vw,1.95rem)] font-bold">Overall Session Score</p>
          <OverallScoreCard score={reportScore} size="large" />
          <p className="mt-[clamp(0.7rem,1.2vh,1rem)] text-center text-[clamp(1.2rem,1.3vw,1.45rem)] font-medium text-[#d8f3ff]">Your overall presence</p>
        </div>
        <div className="min-h-0 overflow-hidden pl-[clamp(0.15rem,0.45vw,0.65rem)]">
          {timeline[0]?.values.length ? (
            <TimelineChart series={timeline} label="Overall session score" yTickInterval={10} />
          ) : (
            <EmptyState title="No timeline yet" message="Timeline data was not returned for this session." />
          )}
        </div>
      </div>
      <div className="mt-[1vh] grid gap-[1vw] sm:grid-cols-2 xl:grid-cols-4">
        {[
          ["Duration", formatDuration(duration), "text-white"],
          ["Trend", trend ?? "N/A", "text-emerald-300"],
          ["Min Score", formatScore(minScore), "text-violet-300"],
          ["Max Score", formatScore(maxScore), "text-sky-300"],
        ].map(([label, value, colorClass]) => (
          <div key={label} className="hud-card grid min-h-[clamp(5rem,10vh,6.5rem)] content-center p-[clamp(0.85rem,1.25vw,1.35rem)]">
            <p className="hud-label text-base">{label}</p>
            <p className={`mt-2 text-[clamp(2rem,3.1vw,3.3rem)] font-bold leading-none ${colorClass}`}>{value}</p>
          </div>
        ))}
      </div>
    </div>
    <div className="hud-panel grid min-h-0 grid-rows-[auto_minmax(0,1fr)] p-[clamp(0.75rem,1vw,1rem)] xl:col-span-2">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="hud-title text-[clamp(1.2rem,1.6vw,1.8rem)] font-bold">Metric Summary</h2>
        <span className="hud-label text-base">Aggregates</span>
      </div>
      <div className="grid min-h-0 gap-[0.8vw] md:grid-cols-5">
        {metrics.map((metric) => (
          <MetricSummaryCard key={metric.key} metric={metric} />
        ))}
      </div>
    </div>
  </>
);
