import type { ReportView } from "../../../domain/sessionAnalysis";
import type { MetricSummaryView, TimelineSeries } from "../dashboard.types";
import { formatScore } from "../utils/formatters";
import { trendFromSeries } from "../utils/trends";
import { AiRecommendationsCard } from "./AiRecommendationsCard";
import { AiSummaryCard } from "./AiSummaryCard";
import { MultiMetricTimeline } from "./MultiMetricTimeline";
import { AUDIO_METRICS, RawMetricCard, VISUAL_METRICS } from "./RawMetricCard";

type DetailedReportViewProps = {
  report: ReportView | null;
  timeline: TimelineSeries[];
  metrics: MetricSummaryView[];
  summary: string | undefined;
  recommendations: string | undefined;
};

const sectionTitle = "hud-title mb-4 border-b border-cyan-300/15 pb-3 text-2xl font-bold";
const scoreOrder = ["focus", "engagement", "posture", "composure", "presence"];

export const DetailedReportView = ({ report, timeline, metrics, summary, recommendations }: DetailedReportViewProps) => (
  <div className="grid min-h-0 min-w-0 grid-rows-[auto_minmax(0,1fr)] gap-3 xl:h-full">
    <header className="flex flex-wrap items-center justify-between gap-2 px-1">
      <h1 className="hud-title text-2xl font-bold tracking-wide">Detailed Analysis</h1>
      <span className="rounded border border-cyan-300/25 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-200">Scroll to explore all metrics ↓</span>
    </header>
    <div className="detailed-analysis-scroll min-h-0 min-w-0 space-y-7 overflow-y-scroll overscroll-contain pr-3 pb-6 outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 max-xl:max-h-[78vh]" tabIndex={0} role="region" aria-label="Detailed analysis, scroll for visual and audio metrics">
      <section className="hud-panel p-5">
        <h2 className={sectionTitle}>1. Overall Performance</h2>
        <div className="mb-5 flex items-center gap-4 rounded border border-emerald-300/20 bg-emerald-400/5 px-4 py-3">
          <span className="text-sm font-semibold text-emerald-100">Overall Score</span>
          <strong className="text-4xl text-emerald-300">{formatScore(report?.overallScore)}</strong>
          <span className="text-sm text-[#9cbfd0]">/ 100</span>
        </div>
        <div className="h-[clamp(18rem,38vh,28rem)]"><MultiMetricTimeline series={timeline} /></div>
      </section>
      <section>
        <h2 className={sectionTitle}>2. AI Coaching</h2>
        <div className="grid gap-4 md:grid-cols-2"><AiSummaryCard text={summary} /><AiRecommendationsCard text={recommendations} /></div>
      </section>
      <section className="hud-panel p-5">
        <h2 className={sectionTitle}>3. Performance Scores</h2>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[490px] text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-cyan-200"><tr>{["Score", "Avg", "Min", "Max", "Trend"].map((title) => <th key={title} scope="col" className="px-3 py-3">{title}</th>)}</tr></thead>
            <tbody>{[...metrics].sort((a, b) => scoreOrder.indexOf(a.key) - scoreOrder.indexOf(b.key)).map((metric) => {
              const trend = metric.summary?.trend?.toLowerCase() ?? trendFromSeries(metric.series).toLowerCase();
              const label = trend === "up" ? "Improving" : trend === "down" ? "Down" : trend === "stable" ? "Stable" : "—";
              return <tr key={metric.key} className="border-t border-cyan-300/10"><th scope="row" className={`px-3 py-4 font-semibold ${metric.tone.valueClass}`}>{metric.label}</th><td className="px-3 py-4">{formatScore(metric.summary?.avg)}</td><td className="px-3 py-4">{formatScore(metric.summary?.min)}</td><td className="px-3 py-4">{formatScore(metric.summary?.max)}</td><td className={`px-3 py-4 ${trend === "up" ? "text-emerald-300" : trend === "down" ? "text-rose-300" : "text-[#9cbfd0]"}`}>{label}</td></tr>;
            })}</tbody>
          </table>
        </div>
      </section>
      <section>
        <h2 className={sectionTitle}>4. Visual Metrics</h2>
        <div className="grid gap-4 md:grid-cols-2">{VISUAL_METRICS.map((definition) => <RawMetricCard key={definition[0]} definition={definition} summary={report?.visualMetrics?.[definition[0]]} timeline={report?.metricSeries} />)}</div>
      </section>
      <section>
        <h2 className={sectionTitle}>5. Audio Metrics</h2>
        <div className="grid gap-4 md:grid-cols-2">{AUDIO_METRICS.map((definition) => <RawMetricCard key={definition[0]} definition={definition} summary={report?.audioMetrics?.[definition[0]]} timeline={report?.metricSeries} />)}</div>
      </section>
    </div>
  </div>
);
