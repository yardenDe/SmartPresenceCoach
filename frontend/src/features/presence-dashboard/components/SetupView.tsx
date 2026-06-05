import type { CoachingMode } from "../dashboard.types";
import { CoachingModeSelector } from "./CoachingModeSelector";

type SetupViewProps = {
  selectedMode: CoachingMode | null;
  customScenario: string;
  onModeChange: (mode: CoachingMode) => void;
  onCustomScenarioChange: (value: string) => void;
};

export const SetupView = ({
  selectedMode,
  customScenario,
  onModeChange,
  onCustomScenarioChange,
}: SetupViewProps) => (
  <div className="hud-panel grid min-h-0 overflow-hidden">
    <CoachingModeSelector
      selectedMode={selectedMode}
      customScenario={customScenario}
      onModeChange={onModeChange}
      onCustomScenarioChange={onCustomScenarioChange}
    />
  </div>
);
