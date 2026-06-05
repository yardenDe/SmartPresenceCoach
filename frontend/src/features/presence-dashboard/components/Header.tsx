import type { DashboardState } from "../dashboard.types";

type HeaderProps = {
  state: DashboardState;
  username: string | null;
};

const stateLabel: Record<DashboardState, string> = {
  setup: "Setup",
  live: "Live Presence Analysis",
  offline_processing: "Processing Video",
  summary: "Session Summary",
  detailed: "Detailed Analysis",
};

export const Header = ({ state, username }: HeaderProps) => (
  <header className="flex h-full min-h-0 items-center justify-between gap-5 px-[0.6vw] py-[0.35vh]">
    <div className="flex min-w-0 items-center gap-5">
      <p className="hud-title truncate text-[clamp(1.1rem,1.35vw,1.5rem)] font-bold">Smart Presence Coach</p>
      <span className="h-7 w-px shrink-0 bg-cyan-300/16" />
      <h1 className="hud-title truncate text-[clamp(1.65rem,2.65vw,3rem)] font-bold">
        {state === "live" ? <span className="text-emerald-300">Live </span> : null}
        {stateLabel[state]}
      </h1>
    </div>
    <p className="hud-title shrink-0 text-[clamp(0.9rem,1.05vw,1.15rem)] font-bold">
      Hello {username ?? "User"} <span className="ml-3 inline-block h-2.5 w-2.5 rounded-full bg-emerald-300" />
    </p>
  </header>
);
