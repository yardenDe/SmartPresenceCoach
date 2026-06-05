type SparklineProps = {
  values: Array<number | null>;
  color: string;
};

export const Sparkline = ({ values, color }: SparklineProps) => {
  const width = 120;
  const height = 34;
  const padding = 4;
  const safeValues = values.length ? values : [null];
  const path = safeValues
    .map((value, index) => {
      const score = Math.max(0, Math.min(100, value ?? 0));
      const x =
        safeValues.length > 1
          ? padding + (index * (width - padding * 2)) / (safeValues.length - 1)
          : width / 2;
      const y = height - padding - (score / 100) * (height - padding * 2);

      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <svg className="block h-full min-h-0 w-full overflow-hidden" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" aria-hidden="true">
      <path d={path} fill="none" stroke={color} strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.4" />
    </svg>
  );
};
