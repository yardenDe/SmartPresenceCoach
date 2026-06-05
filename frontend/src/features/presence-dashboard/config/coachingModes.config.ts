import type { CoachingMode } from "../dashboard.types";

export const COACHING_MODES: Array<{
  id: CoachingMode;
  label: string;
  description: string;
  accent: "emerald" | "sky" | "violet" | "orange";
}> = [
  {
    id: "speech",
    label: "Speech",
    description: "Deliver a speech or talk to an audience",
    accent: "emerald",
  },
  {
    id: "interview",
    label: "Interview",
    description: "Ace your interview with confidence and clarity",
    accent: "sky",
  },
  {
    id: "presentation",
    label: "Presentation",
    description: "Deliver impactful presentations",
    accent: "violet",
  },
  {
    id: "custom",
    label: "Custom",
    description: "Define your own scenario and get tailored insights",
    accent: "orange",
  },
];
