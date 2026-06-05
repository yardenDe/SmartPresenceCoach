import { useMemo, useState } from "react";

import type { CoachingMode, DashboardState, ProcessingStep, SessionSource } from "../dashboard.types";

export const usePresenceDashboard = () => {
  const [dashboardState, setDashboardState] = useState<DashboardState>("setup");
  const [source, setSource] = useState<SessionSource | null>("live_camera");
  const [coachingMode, setCoachingMode] = useState<CoachingMode | null>(null);
  const [customScenario, setCustomScenario] = useState("");
  const [processingStep, setProcessingStep] = useState<ProcessingStep>("uploading");
  const [processingPercent, setProcessingPercent] = useState(0);

  const canStart = useMemo(() => {
    if (!source || !coachingMode) {
      return false;
    }

    if (coachingMode === "custom" && customScenario.trim().length === 0) {
      return false;
    }

    return true;
  }, [coachingMode, customScenario, source]);

  const resetSetup = () => {
    setDashboardState("setup");
    setSource("live_camera");
    setCoachingMode(null);
    setCustomScenario("");
    setProcessingStep("uploading");
    setProcessingPercent(0);
  };

  return {
    dashboardState,
    source,
    coachingMode,
    customScenario,
    processingStep,
    processingPercent,
    canStart,
    setDashboardState,
    setSource,
    setCoachingMode,
    setCustomScenario,
    setProcessingStep,
    setProcessingPercent,
    resetSetup,
  };
};
