export const AiRecommendationsCard = ({ text }: { text: string | undefined }) => (
  <div className="hud-panel min-h-0 overflow-hidden p-[clamp(1rem,1.4vw,1.5rem)]">
    <p className="hud-title text-[clamp(1.25rem,1.8vw,2rem)] font-bold">AI Recommendations</p>
    <p className="mt-3 text-[clamp(1rem,1.2vw,1.25rem)] font-medium leading-8 text-[#eaf8fd]">
      {text || "No AI recommendations were returned for this session."}
    </p>
  </div>
);
