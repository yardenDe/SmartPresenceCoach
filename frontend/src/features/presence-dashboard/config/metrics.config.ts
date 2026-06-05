import type { MetricKey } from "../../../domain/sessionAnalysis";
import type { MetricTone } from "../dashboard.types";

export const METRIC_ORDER: MetricKey[] = [
  "focus",
  "posture",
  "presence",
  "engagement",
  "composure",
];

export const METRIC_CONFIG: Record<MetricKey, { label: string; tone: MetricTone }> = {
  focus: {
    label: "Focus",
    tone: { line: "#38bdf8", valueClass: "text-sky-300", softClass: "bg-sky-400/14", icon: "◎" },
  },
  posture: {
    label: "Posture",
    tone: { line: "#34d399", valueClass: "text-emerald-300", softClass: "bg-emerald-400/14", icon: "⌁" },
  },
  presence: {
    label: "Presence",
    tone: { line: "#a78bfa", valueClass: "text-violet-300", softClass: "bg-violet-400/14", icon: "◌" },
  },
  engagement: {
    label: "Engagement",
    tone: { line: "#fb923c", valueClass: "text-orange-300", softClass: "bg-orange-400/14", icon: "↯" },
  },
  composure: {
    label: "Composure",
    tone: { line: "#22d3ee", valueClass: "text-cyan-300", softClass: "bg-cyan-400/14", icon: "◇" },
  },
};
