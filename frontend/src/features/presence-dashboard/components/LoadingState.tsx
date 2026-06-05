type LoadingStateProps = {
  title: string;
  message: string;
};

export const LoadingState = ({ title, message }: LoadingStateProps) => (
  <div className="grid h-full min-h-0 place-items-center text-center">
    <div className="hud-card w-[min(92%,32rem)] px-6 py-5">
      <p className="hud-title text-[clamp(1.35rem,2vw,2rem)] font-bold">{title}</p>
      <p className="mt-3 text-[clamp(0.95rem,1.1vw,1.1rem)] leading-7 text-[#d8f3ff]/88">{message}</p>
      <div className="mt-5 grid grid-cols-6 gap-2">
        {Array.from({ length: 6 }).map((_, index) => (
          <span key={index} className="h-1.5 rounded-full bg-cyan-300/80 shadow-[0_0_12px_rgba(34,211,238,0.45)]" />
        ))}
      </div>
    </div>
  </div>
);
