const MIME_TYPES = [
  "video/webm;codecs=vp9,opus",
  "video/webm;codecs=vp8,opus",
  "video/webm",
  "video/mp4",
];

const supportedMimeType = () =>
  MIME_TYPES.find((mimeType) => MediaRecorder.isTypeSupported(mimeType));

export const canRecordMediaSegment = () =>
  typeof MediaRecorder !== "undefined" && Boolean(supportedMimeType());

export const recordMediaSegment = (
  stream: MediaStream,
  durationMs: number,
  signal?: AbortSignal,
) =>
  new Promise<Blob>((resolve, reject) => {
    const mimeType = supportedMimeType();

    if (
      !mimeType
      || stream.getVideoTracks().length === 0
      || stream.getAudioTracks().length === 0
    ) {
      reject(new Error("A video and audio stream is required."));
      return;
    }

    const chunks: BlobPart[] = [];
    const recorder = new MediaRecorder(stream, { mimeType });

    const stopTimer = window.setTimeout(() => recorder.stop(), durationMs);

    const abort = () => {
      window.clearTimeout(stopTimer);
      if (recorder.state !== "inactive") {
        recorder.stop();
      }
      reject(new DOMException("Recording was stopped.", "AbortError"));
    };

    signal?.addEventListener("abort", abort, { once: true });

    recorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    });

    recorder.addEventListener("error", () => {
      window.clearTimeout(stopTimer);
      signal?.removeEventListener("abort", abort);
      reject(new Error("The media segment could not be recorded."));
    });

    recorder.addEventListener("stop", () => {
      window.clearTimeout(stopTimer);
      signal?.removeEventListener("abort", abort);

      if (!signal?.aborted) {
        resolve(new Blob(chunks, { type: mimeType }));
      }
    });

    recorder.start();
  });
