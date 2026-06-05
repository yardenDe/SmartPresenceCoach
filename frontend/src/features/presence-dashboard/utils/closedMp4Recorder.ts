type EncodedSample = {
  data: Uint8Array;
  duration: number;
  isKey: boolean;
  timestamp: number;
};

type VideoEncoderChunk = {
  byteLength: number;
  timestamp: number;
  type: "key" | "delta";
  copyTo: (destination: Uint8Array) => void;
};

type VideoEncoderMetadata = {
  decoderConfig?: {
    description?: AllowSharedBufferSource;
  };
};

type VideoEncoderLike = {
  configure: (config: Record<string, unknown>) => void;
  encode: (frame: VideoFrameLike, options?: { keyFrame?: boolean }) => void;
  flush: () => Promise<void>;
  close: () => void;
};

type VideoFrameLike = {
  close: () => void;
};

type WebCodecsWindow = Window &
  typeof globalThis & {
    VideoEncoder?: {
      new (init: {
        output: (chunk: VideoEncoderChunk, metadata?: VideoEncoderMetadata) => void;
        error: (error: Error) => void;
      }): VideoEncoderLike;
      isConfigSupported?: (config: Record<string, unknown>) => Promise<unknown>;
    };
    VideoFrame?: new (
      source: CanvasImageSource,
      init: { timestamp: number; duration?: number },
    ) => VideoFrameLike;
  };

const MP4_TIMESCALE = 90000;
const DEFAULT_FPS = 6;
const MP4_CODEC = "avc1.42E01E";

export const canRecordClosedMp4 = () => {
  const webCodecs = window as WebCodecsWindow;
  return Boolean(webCodecs.VideoEncoder && webCodecs.VideoFrame);
};

export const recordClosedMp4Segment = async (
  video: HTMLVideoElement,
  durationMs: number,
  signal?: AbortSignal,
  fps = DEFAULT_FPS,
) => {
  const webCodecs = window as WebCodecsWindow;

  if (!webCodecs.VideoEncoder || !webCodecs.VideoFrame) {
    throw new Error("This browser cannot create closed MP4 segments.");
  }

  const width = Math.max(2, Math.floor((video.videoWidth || 640) / 2) * 2);
  const height = Math.max(2, Math.floor((video.videoHeight || 480) / 2) * 2);
  const frameDurationUs = Math.round(1_000_000 / fps);
  const sampleDuration = Math.round(MP4_TIMESCALE / fps);
  const samples: EncodedSample[] = [];
  let decoderConfig: Uint8Array | null = null;
  let encoderError: Error | null = null;

  const config = {
    codec: MP4_CODEC,
    width,
    height,
    bitrate: 900_000,
    framerate: fps,
    latencyMode: "realtime" as const,
    avc: { format: "avc" as const },
  };

  if (webCodecs.VideoEncoder.isConfigSupported) {
    const support = (await webCodecs.VideoEncoder.isConfigSupported(config)) as {
      supported?: boolean;
    };

    if (support.supported === false) {
      throw new Error("This browser cannot encode closed H.264 MP4 segments.");
    }
  }

  const encoder = new webCodecs.VideoEncoder({
    output: (chunk, metadata) => {
      if (metadata?.decoderConfig?.description) {
        decoderConfig = new Uint8Array(
          metadata.decoderConfig.description as ArrayBuffer,
        );
      }

      const data = new Uint8Array(chunk.byteLength);
      chunk.copyTo(data);
      samples.push({
        data,
        duration: sampleDuration,
        isKey: chunk.type === "key",
        timestamp: chunk.timestamp,
      });
    },
    error: (error) => {
      encoderError = error;
    },
  });

  encoder.configure(config);

  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");

  if (!context) {
    encoder.close();
    throw new Error("Canvas context is not available.");
  }

  const startedAt = performance.now();
  let frameIndex = 0;

  while (performance.now() - startedAt < durationMs) {
    if (signal?.aborted) {
      encoder.close();
      throw new DOMException("Recording was stopped.", "AbortError");
    }

    context.drawImage(video, 0, 0, width, height);

    const timestamp = frameIndex * frameDurationUs;
    const frame = new webCodecs.VideoFrame(canvas, {
      timestamp,
      duration: frameDurationUs,
    });

    encoder.encode(frame, { keyFrame: frameIndex === 0 });
    frame.close();
    frameIndex += 1;

    const nextFrameAt = startedAt + frameIndex * (1000 / fps);
    await delay(Math.max(0, nextFrameAt - performance.now()));
  }

  await encoder.flush();
  encoder.close();

  if (encoderError) {
    throw encoderError;
  }

  if (!decoderConfig || samples.length === 0) {
    throw new Error("MP4 encoder did not produce a playable segment.");
  }

  samples.sort((first, second) => first.timestamp - second.timestamp);

  return new Blob([muxMp4(samples, decoderConfig, width, height)], {
    type: "video/mp4",
  });
};

const delay = (ms: number) =>
  new Promise<void>((resolve) => {
    window.setTimeout(resolve, ms);
  });

const muxMp4 = (
  samples: EncodedSample[],
  avcConfig: Uint8Array,
  width: number,
  height: number,
) => {
  const ftyp = box(
    "ftyp",
    ascii("isom"),
    u32(0x00000200),
    ascii("isom"),
    ascii("iso2"),
    ascii("avc1"),
    ascii("mp41"),
  );
  const mdatPayload = concat(samples.map((sample) => sample.data));
  const mdat = box("mdat", mdatPayload);
  const firstSampleOffset = ftyp.length + 8;
  const moov = createMoov(samples, avcConfig, width, height, firstSampleOffset);

  return concat([ftyp, mdat, moov]);
};

const createMoov = (
  samples: EncodedSample[],
  avcConfig: Uint8Array,
  width: number,
  height: number,
  firstSampleOffset: number,
) => {
  const mediaDuration = samples.reduce((total, sample) => total + sample.duration, 0);
  const movieDuration = Math.round((mediaDuration / MP4_TIMESCALE) * 1000);

  return box(
    "moov",
    mvhd(movieDuration),
    trak(samples, avcConfig, width, height, mediaDuration, movieDuration, firstSampleOffset),
  );
};

const mvhd = (duration: number) =>
  fullBox(
    "mvhd",
    0,
    0,
    u32(0),
    u32(0),
    u32(1000),
    u32(duration),
    u32(0x00010000),
    u16(0x0100),
    u16(0),
    u32(0),
    u32(0),
    matrix(),
    u32(0),
    u32(0),
    u32(0),
    u32(0),
    u32(0),
    u32(0),
    u32(2),
  );

const trak = (
  samples: EncodedSample[],
  avcConfig: Uint8Array,
  width: number,
  height: number,
  mediaDuration: number,
  movieDuration: number,
  firstSampleOffset: number,
) =>
  box(
    "trak",
    tkhd(width, height, movieDuration),
    mdia(samples, avcConfig, width, height, mediaDuration, firstSampleOffset),
  );

const tkhd = (width: number, height: number, duration: number) =>
  fullBox(
    "tkhd",
    0,
    0x000007,
    u32(0),
    u32(0),
    u32(1),
    u32(0),
    u32(duration),
    u32(0),
    u32(0),
    u16(0),
    u16(0),
    u16(0),
    u16(0),
    matrix(),
    u32(width << 16),
    u32(height << 16),
  );

const mdia = (
  samples: EncodedSample[],
  avcConfig: Uint8Array,
  width: number,
  height: number,
  mediaDuration: number,
  firstSampleOffset: number,
) =>
  box(
    "mdia",
    mdhd(mediaDuration),
    hdlr(),
    minf(samples, avcConfig, width, height, firstSampleOffset),
  );

const mdhd = (duration: number) =>
  fullBox(
    "mdhd",
    0,
    0,
    u32(0),
    u32(0),
    u32(MP4_TIMESCALE),
    u32(duration),
    u16(0x55c4),
    u16(0),
  );

const hdlr = () =>
  fullBox(
    "hdlr",
    0,
    0,
    u32(0),
    ascii("vide"),
    u32(0),
    u32(0),
    u32(0),
    ascii("VideoHandler\0"),
  );

const minf = (
  samples: EncodedSample[],
  avcConfig: Uint8Array,
  width: number,
  height: number,
  firstSampleOffset: number,
) =>
  box(
    "minf",
    fullBox("vmhd", 0, 1, u16(0), u16(0), u16(0), u16(0)),
    dinf(),
    stbl(samples, avcConfig, width, height, firstSampleOffset),
  );

const dinf = () =>
  box(
    "dinf",
    fullBox("dref", 0, 0, u32(1), fullBox("url ", 0, 1)),
  );

const stbl = (
  samples: EncodedSample[],
  avcConfig: Uint8Array,
  width: number,
  height: number,
  firstSampleOffset: number,
) =>
  box(
    "stbl",
    stsd(avcConfig, width, height),
    stts(samples),
    stss(samples),
    stsc(samples),
    stsz(samples),
    stco(firstSampleOffset),
  );

const stsd = (avcConfig: Uint8Array, width: number, height: number) =>
  fullBox(
    "stsd",
    0,
    0,
    u32(1),
    box(
      "avc1",
      zeros(6),
      u16(1),
      u16(0),
      u16(0),
      u32(0),
      u32(0),
      u32(0),
      u16(width),
      u16(height),
      u32(0x00480000),
      u32(0x00480000),
      u32(0),
      u16(1),
      compressorName("WebCodecs AVC"),
      u16(0x0018),
      u16(0xffff),
      box("avcC", avcConfig),
    ),
  );

const stts = (samples: EncodedSample[]) => {
  const entries: Uint8Array[] = [];
  let runCount = 0;
  let currentDuration = samples[0]?.duration ?? 0;

  samples.forEach((sample) => {
    if (sample.duration === currentDuration) {
      runCount += 1;
      return;
    }

    entries.push(u32(runCount), u32(currentDuration));
    currentDuration = sample.duration;
    runCount = 1;
  });

  if (runCount > 0) {
    entries.push(u32(runCount), u32(currentDuration));
  }

  return fullBox("stts", 0, 0, u32(entries.length / 2), ...entries);
};

const stss = (samples: EncodedSample[]) => {
  const keyframes = samples
    .map((sample, index) => (sample.isKey ? index + 1 : 0))
    .filter((sampleNumber) => sampleNumber > 0);

  return fullBox("stss", 0, 0, u32(keyframes.length), ...keyframes.map(u32));
};

const stsc = (samples: EncodedSample[]) =>
  fullBox("stsc", 0, 0, u32(1), u32(1), u32(samples.length), u32(1));

const stsz = (samples: EncodedSample[]) =>
  fullBox(
    "stsz",
    0,
    0,
    u32(0),
    u32(samples.length),
    ...samples.map((sample) => u32(sample.data.length)),
  );

const stco = (firstSampleOffset: number) =>
  fullBox("stco", 0, 0, u32(1), u32(firstSampleOffset));

const matrix = () =>
  concat([
    u32(0x00010000),
    u32(0),
    u32(0),
    u32(0),
    u32(0x00010000),
    u32(0),
    u32(0),
    u32(0),
    u32(0x40000000),
  ]);

const compressorName = (name: string) => {
  const output = new Uint8Array(32);
  const bytes = ascii(name.slice(0, 31));
  output[0] = bytes.length;
  output.set(bytes, 1);
  return output;
};

const fullBox = (
  type: string,
  version: number,
  flags: number,
  ...payloads: Uint8Array[]
) => box(type, u8(version), u24(flags), ...payloads);

const box = (type: string, ...payloads: Uint8Array[]) => {
  const payload = concat(payloads);
  return concat([u32(payload.length + 8), ascii(type), payload]);
};

const concat = (parts: Uint8Array[] | Uint8Array[][]) => {
  const flattened = parts.flat() as Uint8Array[];
  const length = flattened.reduce((total, part) => total + part.length, 0);
  const output = new Uint8Array(length);
  let offset = 0;

  flattened.forEach((part) => {
    output.set(part, offset);
    offset += part.length;
  });

  return output;
};

const ascii = (text: string) => {
  const output = new Uint8Array(text.length);

  for (let index = 0; index < text.length; index += 1) {
    output[index] = text.charCodeAt(index);
  }

  return output;
};

const zeros = (length: number) => new Uint8Array(length);

const u8 = (value: number) => new Uint8Array([value & 0xff]);

const u16 = (value: number) =>
  new Uint8Array([(value >>> 8) & 0xff, value & 0xff]);

const u24 = (value: number) =>
  new Uint8Array([
    (value >>> 16) & 0xff,
    (value >>> 8) & 0xff,
    value & 0xff,
  ]);

const u32 = (value: number) =>
  new Uint8Array([
    (value >>> 24) & 0xff,
    (value >>> 16) & 0xff,
    (value >>> 8) & 0xff,
    value & 0xff,
  ]);
