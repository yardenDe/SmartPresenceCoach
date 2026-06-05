import type { TimelineSeries } from "../dashboard.types";
import { TimelineChart } from "./TimelineChart";

type MultiMetricTimelineProps = {
  series: TimelineSeries[];
};

export const MultiMetricTimeline = ({ series }: MultiMetricTimelineProps) => (
  <div className="grid h-full min-h-0 grid-rows-[minmax(0,1fr)_auto]">
    <div className="min-h-0 overflow-hidden">
      <TimelineChart series={series} label="Overall and metric timeline" />
    </div>
    <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-[clamp(0.8rem,1vw,1rem)] text-[#d8f3ff]">
      {series.map((entry) => (
        <span key={entry.name} className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full" style={{ backgroundColor: entry.color }} />
          {entry.name}
        </span>
      ))}
    </div>
  </div>
);
