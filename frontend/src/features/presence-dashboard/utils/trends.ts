export const trendFromSeries = (series: Array<number | null | undefined>) => {
  const values = series.filter((value): value is number => typeof value === "number");

  if (values.length < 2) {
    return "Waiting";
  }

  const delta = values[values.length - 1] - values[0];

  if (delta > 4) {
    return "Up";
  }

  if (delta < -4) {
    return "Down";
  }

  return "Stable";
};
