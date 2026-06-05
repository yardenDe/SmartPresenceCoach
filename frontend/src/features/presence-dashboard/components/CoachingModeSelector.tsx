import { COACHING_MODES } from "../config/coachingModes.config";
import type { CoachingMode } from "../dashboard.types";

type CoachingModeSelectorProps = {
  selectedMode: CoachingMode | null;
  customScenario: string;
  onModeChange: (mode: CoachingMode) => void;
  onCustomScenarioChange: (value: string) => void;
};

const accentClasses = {
  emerald: {
    idle: "border-emerald-300/25 bg-emerald-400/5 hover:border-emerald-300/55 hover:bg-emerald-400/10",
    selected: "border-emerald-200/85 bg-emerald-400/14 text-emerald-200 shadow-[0_0_28px_rgba(52,211,153,0.2)]",
    icon: "bg-emerald-400/12 text-emerald-200",
  },
  sky: {
    idle: "border-sky-300/25 bg-sky-400/5 hover:border-sky-300/55 hover:bg-sky-400/10",
    selected: "border-sky-200/80 bg-sky-400/14 text-sky-200 shadow-[0_0_28px_rgba(56,189,248,0.18)]",
    icon: "bg-sky-400/12 text-sky-200",
  },
  violet: {
    idle: "border-violet-300/25 bg-violet-400/5 hover:border-violet-300/55 hover:bg-violet-400/10",
    selected: "border-violet-200/80 bg-violet-400/14 text-violet-200 shadow-[0_0_28px_rgba(167,139,250,0.2)]",
    icon: "bg-violet-400/12 text-violet-200",
  },
  orange: {
    idle: "border-orange-300/25 bg-orange-400/5 hover:border-orange-300/55 hover:bg-orange-400/10",
    selected: "border-orange-200/80 bg-orange-400/14 text-orange-200 shadow-[0_0_28px_rgba(251,146,60,0.18)]",
    icon: "bg-orange-400/12 text-orange-200",
  },
};

const modeIcon: Record<CoachingMode, string> = {
  speech: "🎙️",
  interview: "💼",
  presentation: "📊",
  custom: "✎",
};

export const CoachingModeSelector = ({
  selectedMode,
  customScenario,
  onModeChange,
  onCustomScenarioChange,
}: CoachingModeSelectorProps) => {
  const isCustomSelected = selectedMode === "custom";

  return (
    <div className="grid h-full min-h-0 place-items-center overflow-hidden p-[clamp(1rem,2vw,2.25rem)]">
      <div className="grid h-full w-full max-w-[78rem] grid-rows-[auto_minmax(0,1fr)] gap-[clamp(1.1rem,2.3vh,2rem)]">
        <div className="text-center">
          <p className="hud-title text-[clamp(2rem,3vw,3rem)] font-bold leading-tight">Choose Coaching Mode</p>
          <p className="mx-auto mt-3 max-w-[48rem] text-[clamp(1rem,1.2vw,1.25rem)] font-medium leading-7 text-[#d8f3ff]/85">
            Select the type of session you want to analyze.
          </p>
        </div>

        <div className="grid min-h-0 content-center gap-[clamp(0.9rem,1.35vw,1.35rem)] sm:grid-cols-2 xl:grid-cols-4">
          {COACHING_MODES.map((mode) => {
            const selected = selectedMode === mode.id;
            const accent = accentClasses[mode.accent];

            return (
              <button
                key={mode.id}
                type="button"
                onClick={() => onModeChange(mode.id)}
                className={`hud-card grid aspect-[2/3] min-h-0 grid-rows-[auto_minmax(0,1fr)] overflow-hidden px-[clamp(1rem,1.45vw,1.65rem)] py-[clamp(1.05rem,2vh,1.75rem)] text-center transition duration-200 hover:-translate-y-0.5 ${
                  selected ? `${accent.selected} scale-[1.015]` : accent.idle
                }`}
              >
                <span className="flex items-center justify-between gap-3">
                  <span className={`grid aspect-square w-[clamp(4.4rem,6.4vw,7rem)] place-items-center rounded-full ${accent.icon}`}>
                    <span className="text-[clamp(2.4rem,3.8vw,3.8rem)] font-bold leading-none">{modeIcon[mode.id]}</span>
                  </span>
                  <span
                    className={`grid aspect-square w-[clamp(1.45rem,1.7vw,1.8rem)] place-items-center rounded-full border text-[clamp(0.85rem,1vw,1rem)] font-bold transition ${
                      selected ? "border-current bg-white/10 opacity-100" : "border-cyan-200/15 opacity-0"
                    }`}
                    aria-hidden="true"
                  >
                    ✓
                  </span>
                </span>
                <span className="grid min-h-0 content-center justify-items-center">
                  <span className="text-[clamp(1.35rem,1.7vw,1.85rem)] font-bold leading-tight text-[#f2fbff]">{mode.label}</span>
                  <span className="mt-[clamp(0.75rem,1.2vh,1rem)] max-w-[15rem] text-[clamp(0.92rem,1.06vw,1.08rem)] leading-7 text-[#d8f3ff]/86">
                    {mode.description}
                  </span>
                </span>
              </button>
            );
          })}
        </div>

        {isCustomSelected ? (
          <div className="mx-auto grid w-full max-w-[44rem] gap-3 rounded-md border border-orange-300/28 bg-orange-400/7 p-[clamp(0.8rem,1.2vw,1.1rem)] shadow-[0_0_22px_rgba(251,146,60,0.1)] transition duration-200">
            <label className="text-center text-[clamp(0.85rem,1vw,1rem)] font-semibold text-orange-100/90">
              Describe your scenario
            </label>
            <input
              type="text"
              value={customScenario}
              onChange={(event) => onCustomScenarioChange(event.target.value)}
              placeholder="E.g., Sales pitch to investors, team meeting, podcast recording..."
              className="hud-input w-full px-5 py-[clamp(0.85rem,1.3vh,1rem)] text-[clamp(0.9rem,1vw,1.05rem)]"
            />
          </div>
        ) : null}
      </div>
    </div>
  );
};
