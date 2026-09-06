const MEDIA_MIME_TYPES = [
  "video/webm;codecs=vp8,opus",
  "video/webm;codecs=vp9,opus",
  "video/webm",
  "video/mp4",
] as const;

const supportedMimeType = () =>
  MEDIA_MIME_TYPES.find((type) => MediaRecorder.isTypeSupported(type));

export const canRecordMediaSegment = () =>
  typeof MediaRecorder !== "undefined" && Boolean(supportedMimeType());

export const recordMediaSegment = (
  stream: MediaStream,
  durationMs: number,
  signal?: AbortSignal,
) =>
  new Promise<Blob>((resolve, reject) => {
    const mimeType = supportedMimeType();

    if (!mimeType) {
      reject(new Error("This browser cannot record video with audio."));
      return;
    }

    const recorder = new MediaRecorder(stream, { mimeType });
    const chunks: BlobPart[] = [];
    let aborted = false;

    const stop = () => {
      if (recorder.state !== "inactive") recorder.stop();
    };
    const timeoutId = window.setTimeout(stop, durationMs);

    signal?.addEventListener("abort", () => {
      aborted = true;
      stop();
    }, { once: true });

    recorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) chunks.push(event.data);
    });
    recorder.addEventListener("error", () => {
      window.clearTimeout(timeoutId);
      reject(new Error("Media recording failed."));
    });
    recorder.addEventListener("stop", () => {
      window.clearTimeout(timeoutId);

      if (aborted) {
        reject(new DOMException("Recording was stopped.", "AbortError"));
        return;
      }

      resolve(new Blob(chunks, { type: recorder.mimeType }));
    });

    recorder.start();
  });
