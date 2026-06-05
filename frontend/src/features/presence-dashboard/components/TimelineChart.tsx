import { useEffect, useMemo, useRef, useState } from "react";

import type { TimelineSeries } from "../dashboard.types";

type TimelineChartProps = {
  series: TimelineSeries[];
  label: string;
  yTickInterval?: number;
};

const BASE_WIDTH = 900;
const BASE_HEIGHT = 260;
const BASE_PADDING_LEFT = 40;
const BASE_PADDING_RIGHT = 10;
const BASE_PADDING_TOP = 22;
const BASE_PADDING_BOTTOM = 42;
const BASE_FONT_SIZE = 13;
const BASE_STROKE_WIDTH = 3;
const TIME_TICK_SECONDS = 3;

type ChartSize = {
  width: number;
  height: number;
};

type ChartFrame = ChartSize & {
  paddingLeft: number;
  paddingRight: number;
  paddingTop: number;
  paddingBottom: number;
  fontSize: number;
  lineStrokeWidth: number;
  pathStrokeWidth: number;
};

const seriesTimes = (entry: TimelineSeries) =>
  entry.times?.length === entry.values.length
    ? entry.times
    : Array.from({ length: entry.values.length }, (_, index) => index);

const buildChartFrame = ({ width, height }: ChartSize): ChartFrame => {
  const safeWidth = Math.max(1, width);
  const safeHeight = Math.max(1, height);
  const widthScale = safeWidth / BASE_WIDTH;
  const heightScale = safeHeight / BASE_HEIGHT;
  const balancedScale = Math.sqrt(widthScale * heightScale);

  return {
    width: safeWidth,
    height: safeHeight,
    paddingLeft: Math.max(BASE_PADDING_LEFT * widthScale, BASE_FONT_SIZE * balancedScale * 2.6),
    paddingRight: BASE_PADDING_RIGHT * widthScale,
    paddingTop: BASE_PADDING_TOP * heightScale,
    paddingBottom: Math.max(BASE_PADDING_BOTTOM * heightScale, BASE_FONT_SIZE * balancedScale * 2.9),
    fontSize: BASE_FONT_SIZE * balancedScale,
    lineStrokeWidth: Math.max(1, balancedScale),
    pathStrokeWidth: BASE_STROKE_WIDTH * balancedScale,
  };
};

const chartX = (seconds: number, maxSeconds: number, frame: ChartFrame) =>
  frame.paddingLeft +
  (seconds / Math.max(1, maxSeconds)) * (frame.width - frame.paddingLeft - frame.paddingRight);

const maxSeriesTime = (series: TimelineSeries[]) =>
  Math.max(
    0,
    ...series.flatMap((entry) => {
      const times = seriesTimes(entry);
      return times.length ? [times[times.length - 1] ?? 0] : [];
    }),
  );

const chartY = (score: number, frame: ChartFrame) =>
  frame.height -
  frame.paddingBottom -
  (score / 100) * (frame.height - frame.paddingTop - frame.paddingBottom);

const buildPath = (entry: TimelineSeries, maxSeconds: number, frame: ChartFrame) =>
  entry.values
    .map((value, index) => {
      const score = Math.max(0, Math.min(100, value ?? 0));
      const x = chartX(seriesTimes(entry)[index] ?? index, maxSeconds, frame);
      const y = chartY(score, frame);

      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

const formatTime = (seconds: number) => {
  const safeSeconds = Math.max(0, Math.round(seconds));
  const minutes = Math.floor(safeSeconds / 60);
  const rest = safeSeconds % 60;

  return `${minutes}:${rest.toString().padStart(2, "0")}`;
};

const buildTickInterval = (maxSeconds: number, frame: ChartFrame) => {
  const plotWidth = Math.max(1, frame.width - frame.paddingLeft - frame.paddingRight);
  const targetTickCount = Math.max(2, Math.floor(plotWidth / (frame.fontSize * 4.8)));
  const rawInterval = maxSeconds / targetTickCount;
  const intervals = [TIME_TICK_SECONDS, 5, 10, 15, 30, 60, 120, 300];

  return intervals.find((interval) => interval >= rawInterval) ?? intervals[intervals.length - 1];
};

const buildTimeTicks = (series: TimelineSeries[], frame: ChartFrame) => {
  const maxSeconds = maxSeriesTime(series);

  if (maxSeconds <= 0) {
    return [];
  }

  const tickInterval = buildTickInterval(maxSeconds, frame);
  const tickCount = Math.floor(maxSeconds / tickInterval) + 1;
  const ticks = Array.from({ length: tickCount }, (_, index) => index * tickInterval);
  const lastTick = ticks[ticks.length - 1] ?? 0;

  if (lastTick < maxSeconds) {
    ticks.push(Math.ceil(maxSeconds));
  }

  return ticks.map((seconds) => {
    return {
      key: seconds.toString(),
      x: chartX(seconds, maxSeconds, frame),
      label: formatTime(seconds),
    };
  });
};

const buildScoreTicks = (interval?: number) => {
  if (!interval) {
    return [0, 50, 100];
  }

  const safeInterval = Math.max(1, Math.min(100, Math.round(interval)));
  const ticks = Array.from(
    { length: Math.floor(100 / safeInterval) + 1 },
    (_, index) => index * safeInterval,
  );

  if (ticks[ticks.length - 1] !== 100) {
    ticks.push(100);
  }

  return ticks;
};

const scoreGridOpacity = (tick: number, isDense: boolean) => {
  if (!isDense || tick === 0 || tick === 50 || tick === 100) {
    return 0.12;
  }

  return 0.07;
};

const useChartSize = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<ChartSize>({ width: BASE_WIDTH, height: BASE_HEIGHT });

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const syncSize = () => {
      const { width, height } = container.getBoundingClientRect();

      setSize({ width: Math.max(1, width), height: Math.max(1, height) });
    };

    syncSize();

    const observer = new ResizeObserver(syncSize);
    observer.observe(container);

    return () => {
      observer.disconnect();
    };
  }, []);

  return { containerRef, size };
};

export const TimelineChart = ({ series, label, yTickInterval }: TimelineChartProps) => {
  const maxSeconds = maxSeriesTime(series);
  const { containerRef, size } = useChartSize();
  const frame = useMemo(() => buildChartFrame(size), [size]);
  const timeTicks = useMemo(() => buildTimeTicks(series, frame), [series, frame]);
  const scoreTicks = useMemo(() => buildScoreTicks(yTickInterval), [yTickInterval]);
  const hasDenseScoreTicks = scoreTicks.length > 3;

  return (
    <div ref={containerRef} className="h-full min-h-0 w-full overflow-hidden">
      <svg
        className="block h-full max-h-full min-h-0 w-full overflow-hidden"
        viewBox={`0 0 ${frame.width} ${frame.height}`}
        role="img"
        aria-label={label}
      >
        {scoreTicks.map((tick) => {
          const y = chartY(tick, frame);

          return (
            <g key={tick}>
              <line
                x1={frame.paddingLeft}
                x2={frame.width - frame.paddingRight}
                y1={y}
                y2={y}
                stroke={`rgba(216,243,255,${scoreGridOpacity(tick, hasDenseScoreTicks)})`}
                strokeWidth={frame.lineStrokeWidth}
              />
              <text x={frame.fontSize * 0.45} y={y + frame.fontSize * 0.32} fill="#9cbfd0" fontSize={frame.fontSize} fontWeight="600">
                {tick}
              </text>
            </g>
          );
        })}
        {timeTicks.map((tick) => (
          <g key={tick.key}>
            <line
              x1={tick.x}
              x2={tick.x}
              y1={frame.paddingTop}
              y2={frame.height - frame.paddingBottom}
              stroke="rgba(216,243,255,0.06)"
              strokeWidth={frame.lineStrokeWidth}
            />
            <text
              x={tick.x}
              y={frame.height - frame.fontSize * 0.9}
              fill="#9cbfd0"
              fontSize={frame.fontSize}
              fontWeight="600"
              textAnchor="middle"
            >
              {tick.label}
            </text>
          </g>
        ))}
        {series.map((entry) => (
          <path
            key={entry.name}
            d={buildPath(entry, maxSeconds, frame)}
            fill="none"
            stroke={entry.color}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={frame.pathStrokeWidth}
          />
        ))}
      </svg>
    </div>
  );
};
