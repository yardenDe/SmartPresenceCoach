import type { MetricSummaryView, TimelineSeries } from "../dashboard.types";
import { AiRecommendationsCard } from "./AiRecommendationsCard";
import { AiSummaryCard } from "./AiSummaryCard";
import { MetricBreakdownTable } from "./MetricBreakdownTable";
import { MultiMetricTimeline } from "./MultiMetricTimeline";

type DetailedReportViewProps = {
  timeline: TimelineSeries[];
  metrics: MetricSummaryView[];
  summary: string | undefined;
  recommendations: string | undefined;
};

export const DetailedReportView = ({
  timeline,
  metrics,
  summary,
  recommendations,
}: DetailedReportViewProps) => (
  <div className="grid min-h-0 gap-[1vh] xl:grid-rows-[minmax(0,24fr)_minmax(0,46fr)_minmax(0,30fr)]">
    <section className="hud-panel grid min-h-0 grid-rows-[auto_minmax(0,1fr)] p-[clamp(0.85rem,1.15vw,1.2rem)]">
      <h2 className="hud-title text-[clamp(1.05rem,1.35vw,1.55rem)] font-bold">Overall & Metrics Timeline</h2>
      <div className="mt-[clamp(0.45rem,0.8vh,0.7rem)] min-h-0">
        <MultiMetricTimeline series={timeline} />
      </div>
    </section>
    <section className="grid min-h-0 gap-[1vh] lg:grid-cols-2">
      <AiSummaryCard text={summary} />
      <AiRecommendationsCard text={recommendations} />
    </section>
    <MetricBreakdownTable metrics={metrics} />
  </div>
);
