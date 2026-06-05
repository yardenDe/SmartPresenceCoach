import type { RecentSession } from "../../../domain/sessionAnalysis";
import { formatCoachingMode, formatDuration } from "../utils/formatters";
import type { CoachingMode } from "../dashboard.types";

type RecentSessionsProps = {
  sessions: RecentSession[];
};

const formatDate = (value: string | null) => {
  if (!value) {
    return "Pending";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
};

const formatSessionMode = (mode: string | null) =>
  formatCoachingMode(mode as CoachingMode | null);

const durationSeconds = (session: RecentSession) => {
  if (!session.started_at || !session.ended_at) {
    return null;
  }

  return Math.max(
    0,
    Math.round((new Date(session.ended_at).getTime() - new Date(session.started_at).getTime()) / 1000),
  );
};

export const RecentSessions = ({ sessions }: RecentSessionsProps) => (
  <div className="hud-panel min-h-0 overflow-hidden p-[clamp(0.8rem,1.2vw,1rem)]">
    <p className="hud-label text-base">Recent Sessions</p>
    {sessions.length ? (
      <div className="mt-4 grid gap-3 overflow-hidden">
        {sessions.slice(0, 4).map((session) => {
          const duration = durationSeconds(session);

          return (
            <div key={session.session_id} className="border-b border-cyan-300/10 pb-3 last:border-b-0 last:pb-0">
              <div className="flex items-center justify-between gap-3">
                <p className="text-[clamp(0.95rem,1.1vw,1.15rem)] font-bold text-[#f2fbff]">Session #{session.session_id}</p>
                <span className="hud-value font-bold">{session.overall_score === null ? "--" : Math.round(session.overall_score)}</span>
              </div>
              <div className="mt-1 flex items-center justify-between gap-3 text-sm text-[#d8f3ff]/72">
                <span>{formatDate(session.ended_at ?? session.started_at)}</span>
                <span>{duration === null ? "In progress" : formatDuration(duration)}</span>
              </div>
              <div className="mt-1 flex items-center justify-between gap-3 text-sm text-[#d8f3ff]/72">
                <span>Mode</span>
                <span className="truncate text-right font-semibold text-[#f2fbff]">{formatSessionMode(session.mode)}</span>
              </div>
            </div>
          );
        })}
      </div>
    ) : (
      <div className="grid h-[calc(100%-2rem)] place-items-center text-center">
        <div>
          <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-full border border-cyan-300/18 text-cyan-200/80">○</div>
          <p className="text-base font-bold text-[#f2fbff]">No sessions yet</p>
          <p className="mt-2 text-sm leading-6 text-[#d8f3ff]/72">Start your first analysis to build your session history.</p>
        </div>
      </div>
    )}
  </div>
);
