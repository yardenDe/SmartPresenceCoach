export const clampScore = (value: number | null | undefined) =>
  Math.max(0, Math.min(100, Math.round(value ?? 0)));

export const scoreStatus = (score: number | null | undefined) => {
  if (score === null || score === undefined) {
    return "Waiting";
  }

  if (score >= 80) {
    return "Good";
  }

  if (score >= 60) {
    return "Steady";
  }

  return "Low";
};
