import type { ChangeEvent } from "react";

import type { SessionSource } from "../dashboard.types";

type SourceSelectorProps = {
  source: SessionSource | null;
  disabled: boolean;
  uploadedVideoName: string;
  onSourceChange: (source: SessionSource) => void;
  onFileChange: (file: File) => void;
};

export const SourceSelector = ({
  source,
  disabled,
  uploadedVideoName,
  onSourceChange,
  onFileChange,
}: SourceSelectorProps) => {
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (file) {
      onFileChange(file);
    }
  };

  return (
    <div className="hud-panel min-h-fit p-[clamp(0.8rem,1.2vw,1rem)]">
      <p className="hud-label text-base">Source</p>
      <div className="mt-3 grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={() => onSourceChange("live_camera")}
          disabled={disabled}
          className={`hud-button min-h-12 px-3 py-2 text-base disabled:opacity-50 ${
            source === "live_camera" ? "border-cyan-300 bg-cyan-400/12 text-cyan-100" : ""
          }`}
        >
          Camera
        </button>
        <button
          type="button"
          onClick={() => onSourceChange("uploaded_video")}
          disabled={disabled}
          className={`hud-button min-h-12 px-3 py-2 text-base disabled:opacity-50 ${
            source === "uploaded_video" ? "border-cyan-300 bg-cyan-400/12 text-cyan-100" : ""
          }`}
        >
          Upload
        </button>
      </div>
      {source === "uploaded_video" ? (
        <label className={`hud-button mt-3 block cursor-pointer px-4 py-3 text-center text-base ${disabled ? "pointer-events-none opacity-50" : ""}`}>
          <span className="block truncate">{uploadedVideoName || "Choose video"}</span>
          <input type="file" accept="video/*" onChange={handleFileChange} disabled={disabled} className="hidden" />
        </label>
      ) : null}
    </div>
  );
};
