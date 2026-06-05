import type { CoachingMode, SessionSource } from "../dashboard.types";

export const formatDuration = (seconds: number) => {
  const safeSeconds = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(safeSeconds / 60);
  const remainingSeconds = safeSeconds % 60;

  return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
};

export const formatScore = (value: number | null | undefined) =>
  value === null || value === undefined ? "--" : Math.round(value).toString();

export const formatSource = (source: SessionSource) =>
  source === "live_camera" ? "Live Camera" : "Uploaded Video";

export const formatCoachingMode = (mode: CoachingMode | null) => {
  if (!mode) {
    return "Not selected";
  }

  return mode.replace("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
};
