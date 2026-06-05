import type { LiveSnapshot, ReportView } from "../../../domain/sessionAnalysis";
import { buildLiveMetricViews, buildMetricSummaryViews, buildMultiMetricTimeline, buildOverallTimeline } from "../dashboard.adapters";

export const useMetricSeries = (liveData: LiveSnapshot | null, liveHistory: LiveSnapshot[], report: ReportView | null) => ({
  liveMetrics: buildLiveMetricViews(liveData, liveHistory),
  summaryMetrics: buildMetricSummaryViews(report),
  overallTimeline: buildOverallTimeline(report),
  multiMetricTimeline: buildMultiMetricTimeline(report),
});
