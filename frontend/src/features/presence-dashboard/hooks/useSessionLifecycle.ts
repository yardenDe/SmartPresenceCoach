import { useEffect, useRef, useState } from "react";

import { getApiErrorMessage } from "../../../services/api";
import { sessionAnalysisApi } from "../../../services/sessionAnalysisApi";
import {
  canRecordMediaSegment,
  recordMediaSegment,
} from "../utils/mediaRecorder";
import {
  buildProgressReport,
  toLiveSnapshot,
  toReportView,
  type AnalyzerMode,
  type LiveSnapshot,
  type RecentSession,
  type ReportView,
} from "../../../domain/sessionAnalysis";
import {
  drawHolisticHud,
  type HolisticResults,
} from "../utils/landmarkHud";

type HolisticDetector = {
  setOptions: (options: Record<string, unknown>) => void;
  onResults: (callback: (results: HolisticResults) => void) => void;
  send: (input: { image: HTMLVideoElement }) => Promise<void>;
  close?: () => void;
};

declare global {
  interface Window {
    Holistic?: new (config: { locateFile: (file: string) => string }) => HolisticDetector;
  }
}

const LIVE_CHUNK_MS = 3000;
const FIRST_LIVE_CHUNK_MS = 1000;
const HOLISTIC_FRAME_INTERVAL_MS = 120;
const MEDIAPIPE_HOLISTIC_URL = "https://cdn.jsdelivr.net/npm/@mediapipe/holistic/holistic.js";

type PendingOfflineReport = {
  report: ReportView;
  sessionId: number;
};

export const useSessionLifecycle = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const landmarksCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const sessionIdRef = useRef<number | null>(null);
  const offlineVideoFileRef = useRef<File | null>(null);
  const offlineVideoUrlRef = useRef<string | null>(null);
  const poseRef = useRef<HolisticDetector | null>(null);
  const poseFrameRef = useRef<number | null>(null);
  const lastPoseFrameAtRef = useRef(0);
  const isPoseSendingRef = useRef(false);
  const liveSegmentAbortRef = useRef<AbortController | null>(null);
  const isRecordingRef = useRef(false);
  const liveRequestIdRef = useRef(0);
  const liveResultsRef = useRef<LiveSnapshot[]>([]);
  const offlineVideoEndedRef = useRef(false);
  const pendingOfflineReportRef = useRef<PendingOfflineReport | null>(null);

  const [mode, setMode] = useState<AnalyzerMode>("live");
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [isOfflineVideoReady, setIsOfflineVideoReady] = useState(false);
  const [offlineVideoName, setOfflineVideoName] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [sessionSeconds, setSessionSeconds] = useState(0);
  const [liveData, setLiveData] = useState<LiveSnapshot | null>(null);
  const [finalReport, setFinalReport] = useState<ReportView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);
  const [reportMessage, setReportMessage] = useState<string | null>(null);
  const [isReportGenerating, setIsReportGenerating] = useState(false);
  const [isEmailSending, setIsEmailSending] = useState(false);
  const [recentSessions, setRecentSessions] = useState<RecentSession[]>([]);
  const [reportSessionId, setReportSessionId] = useState<number | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);

  useEffect(() => {
    void refreshRecentSessions();

    return () => {
      stopCamera();
      revokeOfflineVideoUrl();
    };
  }, []);

  const refreshRecentSessions = async () => {
    try {
      const response = await sessionAnalysisApi.getRecentSessions();
      setRecentSessions(response.data);
    } catch {
      setRecentSessions([]);
    }
  };

  const publishOfflineReport = (report: ReportView, sessionId: number) => {
    pendingOfflineReportRef.current = null;
    setFinalReport(report);
    setReportSessionId(sessionId);
    setSessionSeconds(report.timeline[report.timeline.length - 1]?.time ?? 0);
    setError(null);
    setReportMessage("Session summary ready.");
    void refreshRecentSessions();
  };

  const handleOfflineVideoEnded = () => {
    offlineVideoEndedRef.current = true;
    clearFrameInterval();
    setSessionSeconds(Math.floor(videoRef.current?.duration || videoRef.current?.currentTime || 0));

    if (pendingOfflineReportRef.current) {
      publishOfflineReport(
        pendingOfflineReportRef.current.report,
        pendingOfflineReportRef.current.sessionId,
      );
    }
  };

  const getCameraErrorMessage = (cameraError: unknown) => {
    if (!navigator.mediaDevices?.getUserMedia) {
      return "Camera access is not available in this browser. Use localhost/HTTPS and a browser that supports camera capture.";
    }

    if (cameraError instanceof DOMException) {
      if (cameraError.name === "NotAllowedError") {
        return "Camera permission was blocked. Allow camera access in the browser and try again.";
      }

      if (cameraError.name === "NotFoundError") {
        return "No camera was found on this device.";
      }

      if (cameraError.name === "NotReadableError") {
        return "The camera is already in use by another app or browser tab.";
      }
    }

    if (cameraError instanceof Error && cameraError.message) {
      return cameraError.message;
    }

    return "Camera could not be started. Check permissions and device availability.";
  };

  const attachVideoElement = (element: HTMLVideoElement | null) => {
    if (videoRef.current) {
      videoRef.current.onended = null;
    }

    videoRef.current = element;

    if (videoRef.current) {
      videoRef.current.onended = handleOfflineVideoEnded;
    }
  };

  const attachLandmarksCanvasElement = (element: HTMLCanvasElement | null) => {
    landmarksCanvasRef.current = element;
  };

  const clearFrameInterval = () => {
    if (intervalRef.current) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const startElapsedTimer = (getSeconds: () => number) => {
    clearFrameInterval();
    setSessionSeconds(Math.max(0, Math.floor(getSeconds())));
    intervalRef.current = window.setInterval(() => {
      setSessionSeconds(Math.max(0, Math.floor(getSeconds())));
    }, 1000);
  };

  const getLiveTimestamp = () =>
    startTimeRef.current ? (Date.now() - startTimeRef.current) / 1000 : sessionSeconds;

  const resetSessionView = () => {
    setSessionSeconds(0);
    setFinalReport(null);
    setReportSessionId(null);
    setReportError(null);
    setReportMessage(null);
    setLiveData(null);
    liveResultsRef.current = [];
    pendingOfflineReportRef.current = null;
    offlineVideoEndedRef.current = false;
  };

  const loadMediaPipePose = async () => {
    if (window.Holistic) {
      return;
    }

    await new Promise<void>((resolve, reject) => {
      const existingScript = document.querySelector<HTMLScriptElement>(
        `script[src="${MEDIAPIPE_HOLISTIC_URL}"]`,
      );

      if (existingScript) {
        existingScript.addEventListener("load", () => resolve(), { once: true });
        existingScript.addEventListener("error", () => reject(new Error("MediaPipe failed to load.")), {
          once: true,
        });
        return;
      }

      const script = document.createElement("script");
      script.src = MEDIAPIPE_HOLISTIC_URL;
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("MediaPipe failed to load."));
      document.head.appendChild(script);
    });
  };

  const syncLandmarksCanvasSize = () => {
    if (!videoRef.current || !landmarksCanvasRef.current) {
      return;
    }

    const width = videoRef.current.videoWidth || videoRef.current.clientWidth;
    const height = videoRef.current.videoHeight || videoRef.current.clientHeight;

    if (!width || !height) {
      return;
    }

    if (
      landmarksCanvasRef.current.width !== width ||
      landmarksCanvasRef.current.height !== height
    ) {
      landmarksCanvasRef.current.width = width;
      landmarksCanvasRef.current.height = height;
    }
  };

  const drawPoseLandmarks = (results: HolisticResults = {}) => {
    if (!landmarksCanvasRef.current) {
      return;
    }

    syncLandmarksCanvasSize();
    drawHolisticHud(landmarksCanvasRef.current, results);
  };

  const clearLandmarks = () => {
    if (!landmarksCanvasRef.current) {
      return;
    }

    const context = landmarksCanvasRef.current.getContext("2d");
    context?.clearRect(0, 0, landmarksCanvasRef.current.width, landmarksCanvasRef.current.height);
  };

  const stopPoseTracking = () => {
    if (poseFrameRef.current) {
      window.cancelAnimationFrame(poseFrameRef.current);
      poseFrameRef.current = null;
    }

    poseRef.current?.close?.();
    poseRef.current = null;
    isPoseSendingRef.current = false;
    clearLandmarks();
  };

  const startPoseTracking = async () => {
    if (!videoRef.current || poseRef.current) {
      return;
    }

    try {
      await loadMediaPipePose();

      if (!window.Holistic || !videoRef.current) {
        return;
      }

      const pose = new window.Holistic({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`,
      });

      pose.setOptions({
        modelComplexity: 0,
        smoothLandmarks: true,
        refineFaceLandmarks: true,
        minDetectionConfidence: 0.55,
        minTrackingConfidence: 0.5,
      });
      pose.onResults(drawPoseLandmarks);
      poseRef.current = pose;

      const runPoseFrame = () => {
        if (!poseRef.current || !videoRef.current || !streamRef.current) {
          return;
        }

        const now = performance.now();
        const shouldSendFrame =
          now - lastPoseFrameAtRef.current >= HOLISTIC_FRAME_INTERVAL_MS;

        if (!isPoseSendingRef.current && shouldSendFrame && videoRef.current.readyState >= 2) {
          lastPoseFrameAtRef.current = now;
          isPoseSendingRef.current = true;
          void poseRef.current
            .send({ image: videoRef.current })
            .catch(() => clearLandmarks())
            .finally(() => {
              isPoseSendingRef.current = false;
            });
        }

        poseFrameRef.current = window.requestAnimationFrame(runPoseFrame);
      };

      runPoseFrame();
    } catch {
      clearLandmarks();
    }
  };

  const revokeOfflineVideoUrl = () => {
    if (offlineVideoUrlRef.current) {
      URL.revokeObjectURL(offlineVideoUrlRef.current);
      offlineVideoUrlRef.current = null;
    }
  };

  const chooseMode = (nextMode: AnalyzerMode) => {
    if (isAnalyzing) {
      return;
    }

    setMode(nextMode);
    setError(null);
    setSessionSeconds(0);

    if (nextMode === "live") {
      setIsOfflineVideoReady(false);
      setOfflineVideoName("");
      offlineVideoFileRef.current = null;
      pendingOfflineReportRef.current = null;
      offlineVideoEndedRef.current = false;
      revokeOfflineVideoUrl();

      if (videoRef.current) {
        videoRef.current.removeAttribute("src");
        videoRef.current.load();
      }
    } else {
      stopPoseTracking();
      stopCamera();
    }
  };

  const loadOfflineVideo = (file: File) => {
    if (isAnalyzing) {
      return;
    }

    stopCamera();
    stopPoseTracking();
    revokeOfflineVideoUrl();

    const videoUrl = URL.createObjectURL(file);
    offlineVideoFileRef.current = file;
    offlineVideoUrlRef.current = videoUrl;

    if (videoRef.current) {
      videoRef.current.srcObject = null;
      videoRef.current.src = videoUrl;
      videoRef.current.currentTime = 0;
      videoRef.current.load();
    }

    setMode("offline");
    resetSessionView();
    setError(null);
    setOfflineVideoName(file.name);
    setIsOfflineVideoReady(true);
    pendingOfflineReportRef.current = null;
    offlineVideoEndedRef.current = false;
  };

  const startCamera = async () => {
    try {
      revokeOfflineVideoUrl();
      setMode("live");
      setIsOfflineVideoReady(false);
      setOfflineVideoName("");
      offlineVideoFileRef.current = null;
      setReportMessage("Requesting camera access.");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.removeAttribute("src");
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setIsCameraReady(true);
      setError(null);
      setReportMessage("Camera ready.");
      void startPoseTracking();
      return true;
    } catch (cameraError) {
      setIsCameraReady(false);
      setReportMessage(null);
      setError(getCameraErrorMessage(cameraError));
      return false;
    }
  };

  const sendVideoSegment = async (
    segment: Blob,
    timestamp: number,
  ) => {
    if (!sessionIdRef.current) {
      return;
    }

    const requestId = liveRequestIdRef.current + 1;
    liveRequestIdRef.current = requestId;

    try {
      const response = await sessionAnalysisApi.sendLiveSegment(
        sessionIdRef.current,
        segment,
        timestamp,
      );

<<<<<<< Updated upstream
      if (typeof response.data?.result?.overall !== "number") {
=======
      if (typeof response.data?.analysis?.visual?.overall !== "number") {
>>>>>>> Stashed changes
        throw new Error("Live analysis response is not ready yet.");
      }

      if (requestId !== liveRequestIdRef.current) {
        return;
      }

      const nextLiveData = toLiveSnapshot(response.data);
      liveResultsRef.current = [...liveResultsRef.current, nextLiveData];
      setLiveData(nextLiveData);
      setError(null);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    }
  };

  const startLiveChunkRecorder = () => {
    if (!streamRef.current || !sessionIdRef.current || !videoRef.current) {
      return;
    }

    if (!canRecordMediaSegment()) {
      setError("This browser cannot record video with audio.");
      setIsAnalyzing(false);
      return;
    }

    let segmentIndex = 0;

    const recordNextSegment = async () => {
      if (!isRecordingRef.current || !videoRef.current || !sessionIdRef.current) {
        return;
      }

      const abortController = new AbortController();
      liveSegmentAbortRef.current = abortController;
      const segmentTimestamp = getLiveTimestamp();
      const segmentDurationMs = segmentIndex === 0 ? FIRST_LIVE_CHUNK_MS : LIVE_CHUNK_MS;

      try {
        const segment = await recordMediaSegment(
          streamRef.current!,
          segmentDurationMs,
          abortController.signal,
        );

        if (isRecordingRef.current && segment.size > 0) {
          await sendVideoSegment(segment, segmentTimestamp);
          segmentIndex += 1;
        }
      } catch (recordingError) {
        if (!abortController.signal.aborted) {
          setError(
            recordingError instanceof Error
              ? recordingError.message
              : getApiErrorMessage(recordingError),
          );
          setIsAnalyzing(false);
          isRecordingRef.current = false;
        }
      } finally {
        if (liveSegmentAbortRef.current === abortController) {
          liveSegmentAbortRef.current = null;
        }

        if (isRecordingRef.current) {
          void recordNextSegment();
        }
      }
    };

    isRecordingRef.current = true;
    void recordNextSegment();
  };

  const stopLiveChunkRecorder = () => {
    isRecordingRef.current = false;
    liveSegmentAbortRef.current?.abort();
    liveSegmentAbortRef.current = null;
  };

  const loadShortReport = async (sessionId: number): Promise<ReportView> => {
    const response = await sessionAnalysisApi.generateShortReport(sessionId);
    return toReportView(response.data);
  };

  const loadFullReport = async (sessionId: number): Promise<ReportView> => {
    const response = await sessionAnalysisApi.generateFullReport(sessionId);
    return toReportView(response.data);
  };

  const generateFinalReport = async () => {
    if (!reportSessionId || !finalReport || isReportGenerating) {
      return;
    }

    setIsReportGenerating(true);
    setReportError(null);
    setReportMessage(null);

    try {
      setFinalReport(await loadFullReport(reportSessionId));
      setReportMessage("Detailed analysis generated.");
      setError(null);
      void refreshRecentSessions();
    } catch (requestError) {
      setReportError(getApiErrorMessage(requestError));
    } finally {
      setIsReportGenerating(false);
    }
  };

  const sendReportEmail = async (to: string) => {
    if (!reportSessionId || finalReport?.kind !== "full" || isEmailSending) {
      return;
    }

    setIsEmailSending(true);
    setReportError(null);
    setReportMessage(null);

    try {
      await sessionAnalysisApi.sendReportEmail(reportSessionId, to);
      setReportMessage("Detailed analysis email sent.");
      setError(null);
    } catch (requestError) {
      setReportError(getApiErrorMessage(requestError));
    } finally {
      setIsEmailSending(false);
    }
  };

  const downloadReportPdf = async () => {
    if (!reportSessionId || finalReport?.kind !== "full" || isReportGenerating) {
      return;
    }

    setIsReportGenerating(true);
    setReportError(null);
    setReportMessage(null);

    try {
      const response = await sessionAnalysisApi.downloadReportPdf(reportSessionId);
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = `presence-analysis-${reportSessionId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setReportMessage("PDF downloaded.");
      setError(null);
    } catch (requestError) {
      setReportError(getApiErrorMessage(requestError));
    } finally {
      setIsReportGenerating(false);
    }
  };

  const startSession = async (sessionMode: AnalyzerMode = mode, sessionModeContext?: string | null) => {
    if (isAnalyzing || isStarting) {
      return;
    }

    setIsStarting(true);
    const offlineVideoFile = offlineVideoFileRef.current;

    if (sessionMode === "offline") {
      if (!offlineVideoFile) {
        setError("Upload a video before starting an offline analysis.");
        setIsStarting(false);
        return;
      }

      try {
        resetSessionView();
        setError(null);
        setReportMessage("Preparing offline analysis.");
        setIsAnalyzing(true);
        pendingOfflineReportRef.current = null;
        offlineVideoEndedRef.current = false;

        if (videoRef.current) {
          videoRef.current.currentTime = 0;
          void videoRef.current.play().catch(() => undefined);
        }

        startTimeRef.current = Date.now();
        startElapsedTimer(() => videoRef.current?.currentTime ?? 0);

        const createResponse = await sessionAnalysisApi.createSession(sessionModeContext);
        const createdSessionId = createResponse.data;

        setReportMessage("Opening analysis session.");
        await sessionAnalysisApi.startSession(createdSessionId);
        sessionIdRef.current = createdSessionId;

        setReportMessage("Uploading and analyzing video. This can take a few minutes.");
        await sessionAnalysisApi.uploadOfflineVideo(createdSessionId, offlineVideoFile);
        setReportMessage("Finalizing analysis.");
        await sessionAnalysisApi.endSession(createdSessionId);
        setReportMessage("Building session summary.");
        const shortReport = await loadShortReport(createdSessionId);
        sessionIdRef.current = null;

        if (offlineVideoEndedRef.current || videoRef.current?.ended || !videoRef.current) {
          publishOfflineReport(shortReport, createdSessionId);
        } else {
          pendingOfflineReportRef.current = {
            report: shortReport,
            sessionId: createdSessionId,
          };
          setError(null);
          setReportMessage("Analysis is ready. Waiting for the video to finish.");
        }
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : getApiErrorMessage(requestError),
        );
      } finally {
        if (!pendingOfflineReportRef.current || videoRef.current?.ended || !videoRef.current) {
          clearFrameInterval();
        }
        startTimeRef.current = null;
        setIsAnalyzing(false);
        setIsStarting(false);
      }

      return;
    }

    resetSessionView();
    const cameraStarted = await startCamera();

    if (!cameraStarted || !streamRef.current) {
      setIsStarting(false);
      return;
    }

    try {
      const createResponse = await sessionAnalysisApi.createSession(sessionModeContext);
      const createdSessionId = createResponse.data;

      await sessionAnalysisApi.startSession(createdSessionId);

      sessionIdRef.current = createdSessionId;
      startTimeRef.current = Date.now();
      startElapsedTimer(() =>
        startTimeRef.current ? (Date.now() - startTimeRef.current) / 1000 : 0,
      );
      setError(null);
      setReportMessage(null);
      setIsAnalyzing(true);
      startLiveChunkRecorder();
    } catch (requestError) {
      stopCurrentAnalysis();
      setError(getApiErrorMessage(requestError));
      return;
    } finally {
      setIsStarting(false);
    }

  };

  const stopCamera = () => {
    clearFrameInterval();
    stopLiveChunkRecorder();
    stopPoseTracking();

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    setIsCameraReady(false);
    setIsAnalyzing(false);
  };

  const stopCurrentAnalysis = () => {
    clearFrameInterval();

    if (mode === "live") {
      stopLiveChunkRecorder();
      stopCamera();
      return;
    }

    if (videoRef.current) {
      videoRef.current.pause();
    }

    setIsAnalyzing(false);
  };

  const stopSession = async () => {
    if (isStopping) {
      return;
    }

    setIsStopping(true);
    stopCurrentAnalysis();

    try {
      const stoppedSessionId = sessionIdRef.current;

      if (sessionIdRef.current) {
        await sessionAnalysisApi.endSession(sessionIdRef.current);
      }

      const fallbackReport = buildProgressReport(liveResultsRef.current);

      if (stoppedSessionId) {
        const shortReport = await loadShortReport(stoppedSessionId);
        setFinalReport(shortReport);
        setReportSessionId(stoppedSessionId);
        void refreshRecentSessions();
      } else if (fallbackReport) {
        setFinalReport(fallbackReport);
      }

      setError(null);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
      setFinalReport(buildProgressReport(liveResultsRef.current));
    } finally {
      sessionIdRef.current = null;
      setIsStopping(false);
    }
  };

  const resetSession = () => {
    stopCurrentAnalysis();
    sessionIdRef.current = null;
    startTimeRef.current = null;
    setMode("live");
    setIsOfflineVideoReady(false);
    setOfflineVideoName("");
    offlineVideoFileRef.current = null;
    pendingOfflineReportRef.current = null;
    offlineVideoEndedRef.current = false;
    revokeOfflineVideoUrl();
    resetSessionView();
    setError(null);
  };

  return {
    videoRef,
    mode,
    offlineVideoName,
    recentSessions,
    liveData,
    liveHistory: liveResultsRef.current,
    finalReport,
    reportError,
    reportMessage,
    isReportGenerating,
    isEmailSending,
    canGenerateReport: Boolean(reportSessionId && finalReport),
    canSendReportEmail: Boolean(reportSessionId && finalReport?.kind === "full"),
    canDownloadReportPdf: Boolean(reportSessionId && finalReport?.kind === "full"),
    isCameraReady,
    isOfflineVideoReady,
    isAnalyzing,
    sessionSeconds,
    error,
    isStarting,
    isStopping,
    attachVideoElement,
    attachLandmarksCanvasElement,
    chooseMode,
    loadOfflineVideo,
    startSession,
    stopSession,
    resetSession,
    generateFinalReport,
    sendReportEmail,
    downloadReportPdf,
  };
};
