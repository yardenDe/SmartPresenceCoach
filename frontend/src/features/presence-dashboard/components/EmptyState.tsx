type EmptyStateProps = {
  title: string;
  message: string;
};

export const EmptyState = ({ title, message }: EmptyStateProps) => (
  <div className="grid h-full min-h-0 place-items-center text-center">
    <div className="max-w-md px-6">
      <div className="mx-auto mb-5 grid aspect-square w-[clamp(3.5rem,8vh,5.25rem)] place-items-center rounded-full border border-cyan-300/18 bg-cyan-400/5 text-3xl text-cyan-200/80">
        ○
      </div>
      <p className="hud-title text-[clamp(1.35rem,2vw,2rem)] font-bold">{title}</p>
      <p className="mt-3 text-[clamp(0.9rem,1.1vw,1.1rem)] leading-7 text-[#d8f3ff]/85">{message}</p>
    </div>
  </div>
);
