import { formatScore } from "../utils/formatters";
import { scoreStatus } from "../utils/score";

type OverallScoreCardProps = {
  score: number | null;
  status?: string;
  size?: "default" | "panel" | "large";
};

export const OverallScoreCard = ({ score, status, size = "default" }: OverallScoreCardProps) => {
  const safeScore = Math.max(0, Math.min(100, score ?? 0));
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - safeScore / 100);
  const circleClass =
    size === "large"
      ? "w-[92%]"
      : size === "panel"
        ? "w-[78%]"
        : "w-[70%]";
  const valueClass =
    size === "large"
      ? "text-[34cqw]"
      : size === "panel"
        ? "text-[32cqw]"
        : "text-[31cqw]";
  const statusClass =
    size === "large"
      ? "text-[10cqw]"
      : "text-[8cqw]";

  return (
    <div className="grid min-h-0 w-full place-items-center text-center [container-type:inline-size]">
      <div className={`relative grid aspect-square place-items-center ${circleClass}`}>
        <svg className="absolute inset-0 h-full w-full -rotate-90" viewBox="0 0 120 120" aria-hidden="true">
          <circle cx="60" cy="60" r={radius} fill="none" stroke="rgba(141,221,242,0.13)" strokeWidth="8" />
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke="#19e6a1"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            strokeWidth="8"
          />
        </svg>
        <div>
          <p className={`hud-value font-bold leading-none ${valueClass}`}>{formatScore(score)}</p>
          <p className="hud-label mt-1 text-[5cqw]">/100</p>
        </div>
      </div>
      <p className={`hud-value mt-[clamp(0.65rem,1.2vh,1rem)] font-bold ${statusClass}`}>
        {status ?? scoreStatus(score)}
      </p>
    </div>
  );
};
