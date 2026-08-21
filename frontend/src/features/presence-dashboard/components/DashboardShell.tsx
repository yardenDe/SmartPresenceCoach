import type { ReactNode } from "react";

import type { DashboardState } from "../dashboard.types";
import { Header } from "./Header";

type DashboardShellProps = {
  state: DashboardState;
  username: string | null;
  leftRail: ReactNode;
  workspace: ReactNode;
};

export const DashboardShell = ({ state, username, leftRail, workspace }: DashboardShellProps) => (
  <section className="grid min-h-0 gap-[1vh] xl:h-full xl:grid-rows-[clamp(3rem,5.6vh,4rem)_minmax(0,1fr)]">
    <Header state={state} username={username} />
    <div className="grid min-h-0 grid-cols-1 gap-[1vh] xl:grid-cols-[minmax(250px,19fr)_minmax(0,81fr)]">
      {leftRail}
      {workspace}
    </div>
  </section>
);
