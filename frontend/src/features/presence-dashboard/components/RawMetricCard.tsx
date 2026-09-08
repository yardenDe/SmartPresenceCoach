import type { BackendRawMetricSummary, BackendTimeSeries } from "../../../domain/sessionAnalysis";

export const VISUAL_METRICS = [
  ["gaze_direction", "Gaze Direction", "How directly you looked forward"],
  ["movement_amount", "Movement Amount", "How much you moved overall"],
  ["movement_variation", "Movement Variation", "How stable your movement was"],
  ["head_movement", "Head Movement", "How much your head moved"],
  ["shoulder_tilt", "Shoulder Tilt", "How level your shoulders stayed"],
  ["hand_movement", "Hand Movement", "How much you used your hands"],
] as const;
export const AUDIO_METRICS = [
  ["pause_ratio", "Pauses", "How much of the session was silent"],
  ["average_volume", "Voice Volume", "How loud you spoke"],
  ["volume_variation", "Volume Variation", "How much your loudness changed"],
  ["pitch_variation", "Pitch Variation", "How much your voice pitch changed"],
] as const;

const finite = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
const numberText = (value: number) => value.toLocaleString("en-US", { maximumFractionDigits: 2 });
const units: Record<string, string> = { deg: "°", "deg/sec": "°/s", ratio: "%", "body-scale/sec": "body-scale/s" };

export const RawMetricCard = ({ definition: [key, title, description], summary, timeline }: {
  definition: readonly [string, string, string];
  summary?: BackendRawMetricSummary;
  timeline?: BackendTimeSeries;
}) => {
  const scale = summary?.unit === "ratio" ? 100 : 1;
  const unit = units[summary?.unit ?? ""] ?? summary?.unit ?? "";
  const format = (value: number) => `${numberText(value)}${["°", "%", "°/s"].includes(unit) ? "" : " "}${unit}`.trim();
  const points = (timeline?.series[key] ?? []).map((value, index) => ({
    value: finite(value) ? value * scale : null,
    time: timeline?.timestamps_sec[index],
  }));
  const available = points.filter((point) => finite(point.value) && finite(point.time));
  const targetMin = finite(summary?.target_min) ? summary.target_min * scale : null;
  const targetMax = finite(summary?.target_max) ? summary.target_max * scale : null;
  const hasTarget = targetMin !== null && targetMax !== null && targetMax >= targetMin;
  const bounds = available.map((point) => point.value as number);
  if (hasTarget) bounds.push(targetMin, targetMax);
  let low = bounds.length ? Math.min(...bounds) : 0;
  let high = bounds.length ? Math.max(...bounds) : 1;
  const padding = Math.max((high - low) * 0.15, Math.abs(high) * 0.03, 0.01);
  low -= padding;
  high += padding;
  const start = Math.min(0, ...available.map((point) => point.time as number));
  const end = Math.max(start + 1, ...available.map((point) => point.time as number));
  const x = (time: number) => 66 + (time - start) / (end - start) * 376;
  const y = (value: number) => 190 - (value - low) / (high - low) * 164;
  let connected = false;
  const path = points.map((point) => {
    if (!finite(point.value) || !finite(point.time)) { connected = false; return ""; }
    const segment = `${connected ? "L" : "M"} ${x(point.time)} ${y(point.value)}`;
    connected = true;
    return segment;
  }).join(" ");

  return (
    <article className="hud-panel min-w-0 p-5">
      <h3 className="hud-title text-xl font-bold">{title}</h3>
      <p className="mt-1 text-sm text-[#9cbfd0]">{description}</p>
      <p className="mt-5 text-xs font-semibold uppercase tracking-widest text-[#9cbfd0]">Average</p>
      <p className="mt-1 text-3xl font-semibold text-cyan-100">{finite(summary?.avg) ? format(summary.avg * scale) : "—"}</p>
      {available.length ? (
        <svg className="mt-4 block w-full" viewBox="0 0 540 230" role="img" aria-label={`${title} over time in ${unit}, with recommended range${hasTarget ? ` ${format(targetMin)} to ${format(targetMax)}` : " unavailable"}`}>
          {hasTarget && <rect x="66" y={y(targetMax)} width="376" height={y(targetMin) - y(targetMax)} fill="#19e6a1" opacity="0.09" />}
          {[0, 1, 2, 3].map((i) => {
            const value = low + (high - low) * i / 3;
            return <g key={i}><line x1="66" x2="442" y1={y(value)} y2={y(value)} stroke="#9cbfd0" opacity="0.15" /><text x="57" y={y(value) + 4} textAnchor="end" fill="#9cbfd0" fontSize="12">{numberText(value)}</text></g>;
          })}
          <path d={path} fill="none" stroke="#39dafa" strokeWidth="2.5" strokeLinejoin="round" />
          {available.length === 1 && <circle cx={x(available[0].time as number)} cy={y(available[0].value as number)} r="4" fill="#39dafa" />}
          {[0, 1, 2, 3].map((i) => { const time = start + (end - start) * i / 3; return <text key={i} x={x(time)} y="217" textAnchor="middle" fill="#9cbfd0" fontSize="12">{numberText(time)}s</text>; })}
          <text x="66" y="14" fill="#9cbfd0" fontSize="11">{unit}</text>
        </svg>
      ) : <div className="mt-4 grid h-48 place-items-center rounded border border-dashed border-cyan-300/20 text-sm text-[#9cbfd0]">No measurements available for this session.</div>}
      <p className="text-xs text-emerald-200/80">{hasTarget ? `Recommended zone: ${format(targetMin)} – ${format(targetMax)}` : "Recommended zone unavailable"}</p>
    </article>
  );
};
