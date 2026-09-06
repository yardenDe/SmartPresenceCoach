import type {
  BackendLiveResponse,
  BackendOfflineResponse,
  BackendReportResponse,
  RecentSession,
  ReportEmailResponse,
} from "../domain/sessionAnalysis";
import { api } from "./api";

const OFFLINE_ANALYSIS_TIMEOUT_MS = 10 * 60 * 1000;
const REPORT_TIMEOUT_MS = 2 * 60 * 1000;

const asMediaFile = (blob: Blob) =>
  new File([blob], blob.type.includes("mp4") ? "live-segment.mp4" : "live-segment.webm", {
    type: blob.type,
  });

export const sessionAnalysisApi = {
  createSession: (mode?: string | null) =>
    api.post<number>("/sessions/create", {
      mode: mode?.trim() || null,
    }),

  getRecentSessions: () => api.get<RecentSession[]>("/reports/recent"),

  startSession: (sessionId: number) =>
    api.post<number>(`/sessions/start/${sessionId}`),

  endSession: (sessionId: number) =>
    api.post<number>(`/sessions/end/${sessionId}`),

  sendLiveSegment: (
    sessionId: number,
    segment: Blob,
    timestamp: number,
  ) => {
    const formData = new FormData();
    formData.append("session_id", String(sessionId));
    formData.append("timestamp", String(timestamp));
    formData.append("video", asMediaFile(segment));

    return api.post<BackendLiveResponse>("/live/chunk", formData);
  },

  uploadOfflineVideo: (sessionId: number, video: File) => {
    const formData = new FormData();
    formData.append("session_id", String(sessionId));
    formData.append("video", video);

    return api.post<BackendOfflineResponse>("/offline/video", formData, {
      timeout: OFFLINE_ANALYSIS_TIMEOUT_MS,
    });
  },

  generateShortReport: (sessionId: number) =>
    api.post<BackendReportResponse>(`/reports/${sessionId}/short`, undefined, {
      timeout: REPORT_TIMEOUT_MS,
    }),

  generateFullReport: (sessionId: number) =>
    api.post<BackendReportResponse>(`/reports/${sessionId}/full`, undefined, {
      timeout: REPORT_TIMEOUT_MS,
    }),

  sendReportEmail: (sessionId: number, to: string) =>
    api.post<ReportEmailResponse>(`/reports/${sessionId}/email`, { to }),

  downloadReportPdf: (sessionId: number) =>
    api.get<Blob>(`/reports/${sessionId}/pdf`, {
      responseType: "blob",
      timeout: REPORT_TIMEOUT_MS,
    }),
};
