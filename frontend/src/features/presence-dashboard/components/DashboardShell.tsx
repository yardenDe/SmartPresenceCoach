import type { ReactNode } from "react";

import { DASHBOARD_LAYOUT } from "../config/theme.tokens";
import type { DashboardState } from "../dashboard.types";
import { Header } from "./Header";

type DashboardShellProps = {
  state: DashboardState;
  username: string | null;
  leftRail: ReactNode;
  workspace: ReactNode;
};

export const DashboardShell = ({ state, username, leftRail, workspace }: DashboardShellProps) => (
  <section
    className="grid h-full min-h-0 gap-[1vh]"
    style={{ gridTemplateRows: `${DASHBOARD_LAYOUT.headerHeight} minmax(0,1fr)` }}
  >
    <Header state={state} username={username} />
    <div
      className="grid min-h-0 gap-[1vh]"
      style={{ gridTemplateColumns: `${DASHBOARD_LAYOUT.leftRailWidth} minmax(0,81fr)` }}
    >
      {leftRail}
      {workspace}
    </div>
  </section>
);
